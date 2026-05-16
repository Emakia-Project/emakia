//
//  TweetViewModel.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//

import Foundation




//
//  TweetViewModel.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//

import Foundation

@MainActor
class TweetViewModel: ObservableObject {
    @Published var tweets: [Tweet] = []
    @Published var neutralTweets: [Tweet] = []
    @Published var harassmentTweets: [Tweet] = []
    @Published var toxicityResults: [String: ToxicityResult] = [:]
    @Published var allModelResults: [String: [ModelVersion: ToxicityResult]] = [:]
    @Published var isClassifying = false
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedModel: ModelVersion = .llm0
    
    private let classifier = ToxicityClassifier()
    private let apiService = APIService.shared
    
    
    func fetch(from platform: SocialPlatform, topic: String, limit: Int, sensitiveFilter: Bool?) async {
        isLoading = true
        errorMessage = nil
        
        do {
            // Fetch tweets from API with search term
            let fetchedTweets = try await apiService.fetchTweets(
                platform: platform,
                topic: topic.trimmingCharacters(in: .whitespacesAndNewlines),
                limit: limit,
                sensitiveFilter: sensitiveFilter
            )
            
            // ✅ Remove duplicates by tweet ID
            var uniqueTweets: [Tweet] = []
            var seenIds = Set<String>()
            
            for tweet in fetchedTweets {
                if !seenIds.contains(tweet.id) {
                    uniqueTweets.append(tweet)
                    seenIds.insert(tweet.id)
                }
            }
            
            self.tweets = uniqueTweets
            print("✅ Fetched \(uniqueTweets.count) unique tweets (removed \(fetchedTweets.count - uniqueTweets.count) duplicates)")
            
            // Classify tweets with all three CoreML models
            await classifyTweetsWithAllModels()
            
            // Send predictions from all models to BigQuery
            await sendAllModelPredictionsToBigQuery()
            
            isLoading = false
        } catch {
            print("❌ Failed to fetch tweets: \(error)")
            if let apiError = error as? APIError {
                errorMessage = apiError.errorDescription
            } else {
                errorMessage = "Failed to fetch tweets: \(error.localizedDescription)"
            }
            isLoading = false
        }
    }
    
    
    /// Classify all tweets using all three CoreML models
    private func classifyTweetsWithAllModels() async {
        isClassifying = true
        
        // Run classification in background
        let results = await Task.detached {
            return await self.classifier.classifyBatchAllModels(tweets: self.tweets)
        }.value
        
        // Update UI on main thread
        self.allModelResults = results
        
        // Set default view to selected model's results
        updateDisplayForSelectedModel()
        
        print("📊 Multi-model classification complete:")
        print("   Total tweets: \(tweets.count)")
        print("   Models evaluated: \(ModelVersion.allCases.count)")
        
        isClassifying = false
    }
    
    /// Update the display based on selected model
    func updateDisplayForSelectedModel() {
        guard !allModelResults.isEmpty else { return }
        
        // Update toxicityResults for backward compatibility with UI
        var selectedResults: [String: ToxicityResult] = [:]
        for (tweetId, modelResults) in allModelResults {
            if let result = modelResults[selectedModel] {
                selectedResults[tweetId] = result
            }
        }
        self.toxicityResults = selectedResults
        
        // Separate tweets based on selected model's classification
        self.neutralTweets = tweets.filter { tweet in
            allModelResults[tweet.id]?[selectedModel]?.isNeutral == true
        }
        
        self.harassmentTweets = tweets.filter { tweet in
            allModelResults[tweet.id]?[selectedModel]?.isHarassment == true
        }
        
        print("📊 Results for \(selectedModel.rawValue):")
        print("   Neutral: \(neutralTweets.count)")
        print("   Harassment: \(harassmentTweets.count)")
    }
    
    /// Send predictions from all three models to BigQuery
    /// ✅ FIXED: Now sends all 3 models in one request per tweet
    private func sendAllModelPredictionsToBigQuery() async {
        guard !allModelResults.isEmpty else {
            print("⚠️ No predictions to send")
            return
        }
        
        print("📤 Sending predictions for \(tweets.count) tweets with all models...")
        
        // ✅ FIX: Use ToxicityClassifier's batchSendPredictions instead of APIService
        // This sends all 3 models' predictions in a single request per tweet
        await classifier.batchSendPredictions(tweets: tweets)
        
        print("✅ All multi-model predictions sent")
    }
}


/*
@MainActor
class TweetViewModel: ObservableObject {
    @Published var tweets: [Tweet] = []
    @Published var neutralTweets: [Tweet] = []
    @Published var harassmentTweets: [Tweet] = []
    @Published var toxicityResults: [String: ToxicityResult] = [:]
    @Published var allModelResults: [String: [ModelVersion: ToxicityResult]] = [:]
    @Published var isClassifying = false
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedModel: ModelVersion = .llm0
    
    private let classifier = ToxicityClassifier()
    private let apiService = APIService.shared
    
    
    func fetch(from platform: SocialPlatform, topic: String, limit: Int, sensitiveFilter: Bool?) async {
        isLoading = true
        errorMessage = nil
        
        do {
            // Fetch tweets from API with search term
            let fetchedTweets = try await apiService.fetchTweets(
                platform: platform,
                topic: topic.trimmingCharacters(in: .whitespacesAndNewlines),
                limit: limit,
                sensitiveFilter: sensitiveFilter
            )
            
            // ✅ Remove duplicates by tweet ID
            var uniqueTweets: [Tweet] = []
            var seenIds = Set<String>()
            
            for tweet in fetchedTweets {
                if !seenIds.contains(tweet.id) {
                    uniqueTweets.append(tweet)
                    seenIds.insert(tweet.id)
                }
            }
            
            self.tweets = uniqueTweets
            print("✅ Fetched \(uniqueTweets.count) unique tweets (removed \(fetchedTweets.count - uniqueTweets.count) duplicates)")
            
            // Classify tweets with all three CoreML models
            await classifyTweetsWithAllModels()
            
            // Send predictions from all models to BigQuery
            await sendAllModelPredictionsToBigQuery()
            
            isLoading = false
        } catch {
            print("❌ Failed to fetch tweets: \(error)")
            if let apiError = error as? APIError {
                errorMessage = apiError.errorDescription
            } else {
                errorMessage = "Failed to fetch tweets: \(error.localizedDescription)"
            }
            isLoading = false
        }
    }
    
    
    /// Classify all tweets using all three CoreML models
    private func classifyTweetsWithAllModels() async {
        isClassifying = true
        
        // Run classification in background
        let results = await Task.detached {
            return await self.classifier.classifyBatchAllModels(tweets: self.tweets)
        }.value
        
        // Update UI on main thread
        self.allModelResults = results
        
        // Set default view to selected model's results
        updateDisplayForSelectedModel()
        
        print("📊 Multi-model classification complete:")
        print("   Total tweets: \(tweets.count)")
        print("   Models evaluated: \(ModelVersion.allCases.count)")
        
        isClassifying = false
    }
    
    /// Update the display based on selected model
    func updateDisplayForSelectedModel() {
        guard !allModelResults.isEmpty else { return }
        
        // Update toxicityResults for backward compatibility with UI
        var selectedResults: [String: ToxicityResult] = [:]
        for (tweetId, modelResults) in allModelResults {
            if let result = modelResults[selectedModel] {
                selectedResults[tweetId] = result
            }
        }
        self.toxicityResults = selectedResults
        
        // Separate tweets based on selected model's classification
        self.neutralTweets = tweets.filter { tweet in
            allModelResults[tweet.id]?[selectedModel]?.isNeutral == true
        }
        
        self.harassmentTweets = tweets.filter { tweet in
            allModelResults[tweet.id]?[selectedModel]?.isHarassment == true
        }
        
        print("📊 Results for \(selectedModel.rawValue):")
        print("   Neutral: \(neutralTweets.count)")
        print("   Harassment: \(harassmentTweets.count)")
    }
    
    /// Send predictions from all three models to BigQuery
    private func sendAllModelPredictionsToBigQuery() async {
        var allPredictions: [PredictionRow] = []
        
        // Iterate through all tweets and all models
        for tweet in tweets {
            guard let modelResults = allModelResults[tweet.id] else { continue }
            
            for (modelVersion, result) in modelResults {
                let prediction = PredictionRow(
                    tweet_id: tweet.id,
                    text: tweet.content,
                    prediction: result.category,
                    score: result.confidence,
                    model_version: modelVersion.rawValue,
                    possibly_sensitive: tweet.possibly_sensitive
                )
                allPredictions.append(prediction)
                
                // Debug logging
                print("🔍 Model: \(modelVersion.rawValue)")
                print("   Tweet ID: \(tweet.id)")
                print("   Prediction: \(result.category)")
                print("   Confidence: \(result.confidence)")
                print("   Possibly Sensitive: \(tweet.possibly_sensitive)")
            }
        }
        
        guard !allPredictions.isEmpty else {
            print("⚠️ No predictions to send")
            return
        }
        
        print("📤 Sending \(allPredictions.count) predictions to BigQuery...")
        print("   (\(tweets.count) tweets × \(ModelVersion.allCases.count) models)")
        
        await apiService.sendPredictionsBatch(allPredictions)
        print("✅ All multi-model predictions sent")
    }
} */
