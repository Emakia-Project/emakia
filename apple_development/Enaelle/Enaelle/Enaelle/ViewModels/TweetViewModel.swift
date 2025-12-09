//
//  TweetViewModel.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//

import Foundation
import SwiftUI

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
            tweets = try JSONDecoder().decode([Tweet].self, from: data)
            
            // Automatically classify tweets after fetching
            await classifyAllTweets()
        } catch {
            print("❌ Error fetching data:", error)
        }
    }
    
    func classifyAllTweets() async {
        isClassifying = true
        
        // Run CoreML classification in background thread to avoid UI blocking
        let tweetsCopy = tweets
        let results = await Task.detached(priority: .userInitiated) {
            return self.classifier.classifyBatch(tweets: tweetsCopy)
        }.value
        
        toxicityResults = results
        isClassifying = false
        
        let harassmentCount = harassmentTweets.count
        let neutralCount = neutralTweets.count
        
        print("✅ Classified \(results.count) tweets:")
        print("   📊 Harassment: \(harassmentCount)")
        print("   ✨ Neutral: \(neutralCount)")
    }
}


