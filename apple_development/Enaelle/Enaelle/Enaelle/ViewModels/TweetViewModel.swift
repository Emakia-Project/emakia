

//
//  TweetViewModel.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//

import Foundation
import SwiftUI

// ✅ API Response wrapper - DEFINED ONLY ONCE
struct TweetAPIResponse: Decodable {
    let count: Int?
    let data: [Tweet]  // ✅ Changed from "tweets" to "data"
    let filters_applied: FilterInfo?
    
    struct FilterInfo: Decodable {
        let topic: String?
        let sensitive_filter: String?
        let limit: Int?
    }
    
    var allTweets: [Tweet] {
        return data  // ✅ Return data instead of tweets
    }
}



@MainActor
class TweetViewModel: ObservableObject {
    @Published var tweets: [Tweet] = []
    @Published var toxicityResults: [String: ToxicityResult] = [:]
    @Published var isClassifying = false
    
    private let classifier = ToxicityClassifier()
    
    var neutralTweets: [Tweet] {
        tweets.filter { tweet in
            guard let result = toxicityResults[tweet.id] else { return false }
            return result.isNeutral
        }
    }
    
    var harassmentTweets: [Tweet] {
        tweets.filter { tweet in
            guard let result = toxicityResults[tweet.id] else { return false }
            return result.isHarassment
        }
    }
    
    // ✅ fetch method - DEFINED ONLY ONCE
    func fetch(from source: SocialPlatform, topic: String, limit: Int, sensitiveFilter: Bool?) async {
        var components = URLComponents(string: source.apiEndpoint)!
        components.queryItems = [
            URLQueryItem(name: "topic", value: topic),
            URLQueryItem(name: "limit", value: "\(limit)")
        ]
        
        if let sensitiveFilter = sensitiveFilter {
            components.queryItems?.append(URLQueryItem(name: "sensitive_filter", value: sensitiveFilter ? "true" : "false"))
        }
        
        do {
            let (data, _) = try await URLSession.shared.data(from: components.url!)
            
            // 🔍 DEBUG: Print raw JSON to see what API returns
            if let jsonString = String(data: data, encoding: .utf8) {
                print("📡 Raw API Response:")
                print(jsonString.prefix(1000)) // First 1000 chars
            }
            
            // Try decoding as wrapper object
            let response = try JSONDecoder().decode(TweetAPIResponse.self, from: data)
            tweets = response.allTweets
            print("✅ Successfully decoded \(tweets.count) tweets from API response object")
            
            // 🔍 DEBUG: Check if name/username/profile_image_url are present
            print("\n📊 Checking first 3 tweets for user data:")
            for (index, tweet) in tweets.prefix(3).enumerated() {
                print("Tweet \(index + 1):")
                print("  ✓ ID: \(tweet.id)")
                print("  ✓ Content: \(tweet.content.prefix(50))...")
                print("  ⚠️ Name: \(tweet.name ?? "❌ NIL")")
                print("  ⚠️ Username: \(tweet.username ?? "❌ NIL")")
                print("  ⚠️ Profile Image: \(tweet.profile_image_url ?? "❌ NIL")")
                print("  ✓ Created At: \(tweet.created_at ?? "❌ NIL")")
                print("")
            }
            
            // Automatically classify tweets after fetching
            await classifyAllTweets()
            
        } catch let decodingError as DecodingError {
            print("❌ Decoding Error:")
            switch decodingError {
            case .typeMismatch(let type, let context):
                print("   Type mismatch: Expected \(type)")
                print("   Context: \(context.debugDescription)")
                print("   Coding path: \(context.codingPath)")
            case .keyNotFound(let key, let context):
                print("   Key '\(key.stringValue)' not found")
                print("   Context: \(context.debugDescription)")
            case .valueNotFound(let type, let context):
                print("   Value of type \(type) not found")
                print("   Context: \(context.debugDescription)")
            case .dataCorrupted(let context):
                print("   Data corrupted: \(context.debugDescription)")
            @unknown default:
                print("   Unknown decoding error: \(decodingError)")
            }
        } catch {
            print("❌ Error fetching data:", error)
        }
    }
    
    func classifyAllTweets() async {
        isClassifying = true
        
        let tweetsCopy = tweets
        let results = await Task.detached(priority: .userInitiated) {
            await self.classifier.classifyBatch(tweets: tweetsCopy)
        }.value
        
        toxicityResults = results
        isClassifying = false
        
        // 🚀 Send predictions to backend for each tweet
        for tweet in tweetsCopy {
            if let result = results[tweet.id] {
                let row = PredictionRow(
                    tweet_id: tweet.id,
                    text: tweet.content,
                    prediction: result.category,
                    score: result.confidence,
                    model_version: "CoreML_v1"
                )
                sendPrediction(row: row)
            }
        }
        
        print("✅ Classified \(results.count) tweets:")
        print("   📊 Harassment: \(harassmentTweets.count)")
        print("   ✨ Neutral: \(neutralTweets.count)")
    }
    
    // Updated sendPrediction function with better error handling
    func sendPrediction(row: PredictionRow) {
        guard let url = URL(string: "https://emakiatech-api-b6fc087f7f4f.herokuapp.com/api/prediction") else {
            print("❌ Invalid prediction URL")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let encoder = JSONEncoder()
            let jsonData = try encoder.encode(row)
            request.httpBody = jsonData
            
            // Debug: Print what we're sending
            if let jsonString = String(data: jsonData, encoding: .utf8) {
                print("📤 Sending prediction for tweet: \(row.tweet_id)")
                print("   Prediction: \(row.prediction), Score: \(row.score)")
            }
            
            URLSession.shared.dataTask(with: request) { data, response, error in
                if let error = error {
                    print("❌ Network error sending prediction: \(error.localizedDescription)")
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    print("❌ Invalid response from server")
                    return
                }
                
                // Parse response body for error details
                var responseBody = ""
                if let data = data, let body = String(data: data, encoding: .utf8) {
                    responseBody = body
                }
                
                switch httpResponse.statusCode {
                case 200...299:
                    print("✅ Prediction saved successfully for tweet: \(row.tweet_id)")
                case 400...499:
                    print("❌ Client error (\(httpResponse.statusCode)) sending prediction:")
                    print("   Tweet ID: \(row.tweet_id)")
                    print("   Response: \(responseBody)")
                case 500...599:
                    print("❌ SERVER ERROR (\(httpResponse.statusCode)) saving prediction:")
                    print("   Tweet ID: \(row.tweet_id)")
                    print("   Response: \(responseBody)")
                    print("   This usually means:")
                    print("   - BigQuery table doesn't exist")
                    print("   - Table schema doesn't match the data")
                    print("   - Database connection issue")
                default:
                    print("⚠️ Unexpected status: \(httpResponse.statusCode)")
                    print("   Response: \(responseBody)")
                }
            }.resume()
        } catch {
            print("❌ Failed to encode prediction data: \(error)")
        }
    }

}
