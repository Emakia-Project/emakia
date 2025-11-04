//
//  ToxicityClassifier.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//

import Foundation
import CoreML
import NaturalLanguage

class ToxicityClassifier {
    private var textClassifier: NLModel?
    
    init() {
        // Load the CoreML Text Classifier model
        // Replace "ToxicityTextClassifier" with your actual .mlmodelc name
        if let modelURL = Bundle.main.url(forResource: "ToxicityTextClassifier", withExtension: "mlmodelc") {
            do {
                self.textClassifier = try NLModel(contentsOf: modelURL)
                print("✅ CoreML Text Classifier loaded successfully")
            } catch {
                print("❌ Failed to load CoreML model: \(error)")
            }
        } else {
            print("❌ CoreML model file not found in bundle")
        }
    }
    
    /// Classifies text using CoreML Text Classifier
    /// Returns ToxicityResult with prediction and confidence
    func classify(text: String) -> ToxicityResult {
        guard let textClassifier = textClassifier else {
            print("⚠️ Text classifier not available")
            return ToxicityResult(isHarassment: false, isNeutral: false, confidence: 0.0, category: "unknown")
        }
        
        // Get prediction from CoreML Text Classifier
        guard let predictedLabel = textClassifier.predictedLabel(for: text) else {
            return ToxicityResult(isHarassment: false, isNeutral: false, confidence: 0.0, category: "unknown")
        }
        
        // Get confidence scores for all labels
        let hypotheses = textClassifier.predictedLabelHypotheses(for: text, maximumCount: 10)
        let confidence = hypotheses[predictedLabel] ?? 0.0
        
        // Check the predicted label (case-insensitive)
        let labelLowercased = predictedLabel.lowercased()
        let isHarassment = labelLowercased.contains("harassment")
        let isNeutral = labelLowercased.contains("neutral")
        
        print("📊 Classified: '\(text.prefix(50))...' → \(predictedLabel) (\(Int(confidence * 100))%)")
        
        return ToxicityResult(
            isHarassment: isHarassment,
            isNeutral: isNeutral,
            confidence: confidence,
            category: predictedLabel
        )
    }
    
    /// Batch classify multiple tweets efficiently
    func classifyBatch(tweets: [Tweet]) -> [String: ToxicityResult] {
        var results: [String: ToxicityResult] = [:]
        
        for tweet in tweets {
            let result = classify(text: tweet.content)
            results[tweet.id] = result
        }
        
        return results
    }
    
    /// Classify with detailed output for debugging
    func classifyDetailed(text: String) -> (result: ToxicityResult, allPredictions: [String: Double]) {
        guard let textClassifier = textClassifier else {
            return (
                ToxicityResult(isHarassment: false, isNeutral: false, confidence: 0.0, category: "unknown"),
                [:]
            )
        }
        
        let hypotheses = textClassifier.predictedLabelHypotheses(for: text, maximumCount: 10)
        let predictedLabel = textClassifier.predictedLabel(for: text) ?? "unknown"
        let confidence = hypotheses[predictedLabel] ?? 0.0
        
        let labelLowercased = predictedLabel.lowercased()
        let isHarassment = labelLowercased.contains("harassment")
        let isNeutral = labelLowercased.contains("neutral")
        
        let result = ToxicityResult(
            isHarassment: isHarassment,
            isNeutral: isNeutral,
            confidence: confidence,
            category: predictedLabel
        )
        
        return (result, hypotheses)
    }
}

struct ToxicityResult {
    let isHarassment: Bool
    let isNeutral: Bool
    let confidence: Double
    let category: String
    
    var confidencePercentage: Int {
        Int(confidence * 100)
    }
}
