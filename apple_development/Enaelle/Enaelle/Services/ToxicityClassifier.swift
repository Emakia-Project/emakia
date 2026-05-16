//
//  ToxicityClassifier.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//

import Foundation
import CoreML
import NaturalLanguage

// MARK: - Model Version Enum
enum ModelVersion: String, CaseIterable {
    case llm0 = "ToxicityTextClassifier0"
    case llm3 = "ToxicityTextClassifier3"
    case llm4 = "ToxicityTextClassifier4"
    
    var displayName: String {
        switch self {
        case .llm0: return "Original Labels"
        case .llm3: return "≥3 LLMs Corrections"
        case .llm4: return "≥4 LLMs Corrections"
        }
    }
}

// MARK: - Toxicity Result
struct ToxicityResult {
    let isHarassment: Bool
    let isNeutral: Bool
    let confidence: Double
    let category: String
    let modelVersion: String
    
    var confidencePercentage: Int {
        Int(confidence * 100)
    }
}

// MARK: - Toxicity Classifier
class ToxicityClassifier {
    private var classifiers: [ModelVersion: NLModel] = [:]
    
    init() {
        // Load all three CoreML Text Classifier models
        for version in ModelVersion.allCases {
            if let modelURL = Bundle.main.url(forResource: version.rawValue, withExtension: "mlmodelc") {
                do {
                    classifiers[version] = try NLModel(contentsOf: modelURL)
                    print("✅ Loaded \(version.displayName) model successfully")
                } catch {
                    print("❌ Failed to load \(version.rawValue): \(error)")
                }
            } else {
                print("❌ Model file not found: \(version.rawValue).mlmodelc")
            }
        }
    }
    
    /// Classifies text using a specific model version
    func classify(text: String, using version: ModelVersion) -> ToxicityResult {
        guard let textClassifier = classifiers[version] else {
            print("⚠️ Text classifier not available for \(version.rawValue)")
            return ToxicityResult(
                isHarassment: false,
                isNeutral: false,
                confidence: 0.0,
                category: "unknown",
                modelVersion: version.rawValue
            )
        }
        
        guard let predictedLabel = textClassifier.predictedLabel(for: text) else {
            return ToxicityResult(
                isHarassment: false,
                isNeutral: false,
                confidence: 0.0,
                category: "unknown",
                modelVersion: version.rawValue
            )
        }
        
        let hypotheses = textClassifier.predictedLabelHypotheses(for: text, maximumCount: 10)
        let confidence = hypotheses[predictedLabel] ?? 0.0
        
        let labelLowercased = predictedLabel.lowercased()
        let isHarassment = labelLowercased.contains("harassment")
        let isNeutral = labelLowercased.contains("neutral")
        
        return ToxicityResult(
            isHarassment: isHarassment,
            isNeutral: isNeutral,
            confidence: confidence,
            category: predictedLabel,
            modelVersion: version.rawValue
        )
    }
    
    /// Classifies text using all three models
    func classifyWithAllModels(text: String) -> [ModelVersion: ToxicityResult] {
        var results: [ModelVersion: ToxicityResult] = [:]
        
        for version in ModelVersion.allCases {
            results[version] = classify(text: text, using: version)
        }
        
        return results
    }
    
    /// Batch classify multiple tweets with all models
    func classifyBatchAllModels(tweets: [Tweet]) -> [String: [ModelVersion: ToxicityResult]] {
        var results: [String: [ModelVersion: ToxicityResult]] = [:]
        
        for tweet in tweets {
            results[tweet.id] = classifyWithAllModels(text: tweet.content)
        }
        
        return results
    }
    
    /// Legacy method for backward compatibility - uses LLM0 model
    func classify(text: String) -> ToxicityResult {
        return classify(text: text, using: .llm0)
    }
    
    /// Legacy batch method - uses LLM0 model
    func classifyBatch(tweets: [Tweet]) -> [String: ToxicityResult] {
        var results: [String: ToxicityResult] = [:]
        
        for tweet in tweets {
            let result = classify(text: tweet.content, using: .llm0)
            results[tweet.id] = result
        }
        
        return results
    }
    
    /// Check which models are loaded and available
    func getLoadedModels() -> [ModelVersion] {
        return classifiers.keys.sorted { $0.rawValue < $1.rawValue }
    }
    
    /// Verify models are working with a test classification
    func testModels() {
        let testText = "This is a test message"
        print("🧪 Testing models with: '\(testText)'")
        
        for version in ModelVersion.allCases {
            let result = classify(text: testText, using: version)
            print("   \(version.displayName): \(result.category) (\(result.confidencePercentage)%)")
        }
    }
}

// MARK: - API Client Extension
extension ToxicityClassifier {
    
    /// Send all model predictions to the backend API
    func sendPredictionsToAPI(tweet: Tweet, results: [ModelVersion: ToxicityResult]) async throws {
        let finalResults: [ModelVersion: ToxicityResult]
        if results.isEmpty {
            finalResults = classifyWithAllModels(text: tweet.content)
        } else {
            finalResults = results
        }
        
        guard let url = URL(string: "https://emakiatech-api-b6fc087f7f4f.herokuapp.com/api/prediction") else {
            throw NSError(domain: "Invalid URL", code: -1, userInfo: nil)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        var predictions: [String: [String: Any]] = [:]
        
        for (version, result) in finalResults {
            let versionKey: String
            switch version {
            case .llm0: versionKey = "llm0"
            case .llm3: versionKey = "llm3"
            case .llm4: versionKey = "llm4"
            }
            predictions[versionKey] = [
                "prediction": result.category,
                "score": result.confidence
            ]
        }
        
        guard !predictions.isEmpty else {
            throw NSError(domain: "No predictions", code: -1, userInfo: [NSLocalizedDescriptionKey: "No model predictions available"])
        }
        
        let payload: [String: Any] = [
            "tweet_id": tweet.id,
            "text": tweet.content,
            "possibly_sensitive": tweet.possibly_sensitive as Bool,
            "predictions": predictions
        ]
        
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: payload)
            request.httpBody = jsonData
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NSError(domain: "Invalid response", code: -1, userInfo: nil)
            }
            
            if httpResponse.statusCode == 200 {
                if let responseString = String(data: data, encoding: .utf8) {
                    print("✅ Predictions sent — Tweet ID: \(tweet.id) | Response: \(responseString)")
                }
            } else {
                let errorText = String(data: data, encoding: .utf8) ?? "Unknown error"
                throw NSError(
                    domain: "API Error",
                    code: httpResponse.statusCode,
                    userInfo: [
                        NSLocalizedDescriptionKey: errorText,
                        "statusCode": httpResponse.statusCode
                    ]
                )
            }
        } catch let error as NSError {
            print("❌ Network error: \(error.localizedDescription)")
            throw error
        }
    }
    
    /// Convenience method to classify and send in one call
    func classifyAndSendToAPI(tweet: Tweet) async throws {
        let results = classifyWithAllModels(text: tweet.content)
        try await sendPredictionsToAPI(tweet: tweet, results: results)
    }
    
    /// Batch send predictions for multiple tweets
    func batchSendPredictions(tweets: [Tweet]) async {
        print("🚀 Starting batch prediction for \(tweets.count) tweets")
        
        for (index, tweet) in tweets.enumerated() {
            print("📊 Processing tweet \(index + 1)/\(tweets.count): \(tweet.id)")
            
            let results = classifyWithAllModels(text: tweet.content)
            
            do {
                try await sendPredictionsToAPI(tweet: tweet, results: results)
                print("   ✅ Prediction sent successfully")
                try? await Task.sleep(nanoseconds: 100_000_000) // 0.1 second
            } catch {
                print("   ❌ Failed to send prediction: \(error)")
            }
        }
        
        print("✅ Batch processing complete")
    }
}
