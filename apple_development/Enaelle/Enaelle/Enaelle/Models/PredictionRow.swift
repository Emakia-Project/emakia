//
//  PredictionRow.swift
//  Enaelle
//
//  Created by Corinne David on 12/13/25.
//

import Foundation


struct PredictionRow: Codable {
    let tweet_id: String
    let text: String
    let prediction: String
    let score: Double
    let model_version: String
}

func sendPrediction(row: PredictionRow) {
    guard let url = URL(string: "https://emakiatech-api-b6fc087f7f4f.herokuapp.com/api/prediction") else { return }

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.addValue("application/json", forHTTPHeaderField: "Content-Type")

    do {
        let jsonData = try JSONEncoder().encode(row)
        request.httpBody = jsonData
    } catch {
        print("❌ Failed to encode prediction: \(error)")
        return
    }

    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            print("❌ Error sending prediction: \(error)")
            return
        }
        if let httpResponse = response as? HTTPURLResponse {
            print("✅ Prediction sent, status: \(httpResponse.statusCode)")
        }
    }.resume()
}
