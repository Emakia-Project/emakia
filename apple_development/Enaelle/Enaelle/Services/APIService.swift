//
//  APIService.swift
//  Enaelle
//
//  Created by Corinne David on 1/7/26.
//


import Foundation

class APIService {
    static let shared = APIService()
    
    private init() {}
    
    // MARK: - Fetch Tweets
    
    /// Fetch tweets from BigQuery with optional search term
    func fetchTweets(
        platform: SocialPlatform,
        topic: String,
        limit: Int,
        sensitiveFilter: Bool?
    ) async throws -> [Tweet] {
        // Build URL with query parameters
        var components = URLComponents(string: platform.apiEndpoint)!
        
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "limit", value: String(limit))
        ]
        
        // Add topic if not empty
        let trimmedTopic = topic.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmedTopic.isEmpty {
            queryItems.append(URLQueryItem(name: "topic", value: trimmedTopic))
        }
        
        // Add sensitive filter if specified
        if let sensitiveFilter = sensitiveFilter {
            queryItems.append(URLQueryItem(name: "sensitive_filter", value: String(sensitiveFilter)))
        }
        
        components.queryItems = queryItems
        
        guard let url = components.url else {
            throw APIError.invalidURL
        }
        
        print("🌐 Fetching tweets from: \(url.absoluteString)")
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        print("📡 Response status: \(httpResponse.statusCode)")
        
        guard httpResponse.statusCode == 200 else {
            // Try to parse error message from response
            if let errorData = try? JSONDecoder().decode([String: String].self, from: data),
               let errorMessage = errorData["error"] {
                throw APIError.serverError(statusCode: httpResponse.statusCode, message: errorMessage)
            }
            throw APIError.serverError(statusCode: httpResponse.statusCode, message: nil)
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        let apiResponse = try decoder.decode(TweetResponse.self, from: data)
        
        print("✅ Received \(apiResponse.count) tweets from API")
        if let filters = apiResponse.filtersApplied {
            print("📊 Filters applied - Topic: '\(filters.topic ?? "none")', Limit: \(filters.limit)")
        }
        
        return apiResponse.data
    }
    
    // MARK: - Send Predictions
    
    /// Send prediction to BigQuery (async/await version)
    func sendPrediction(row: PredictionRow) async throws {
        guard let url = URL(string: "https://emakiatech-api-b6fc087f7f4f.herokuapp.com/api/prediction") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        let jsonData = try JSONEncoder().encode(row)
        request.httpBody = jsonData

        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            if let errorData = try? JSONDecoder().decode([String: String].self, from: data),
               let errorMessage = errorData["error"] {
                throw APIError.serverError(statusCode: httpResponse.statusCode, message: errorMessage)
            }
            throw APIError.serverError(statusCode: httpResponse.statusCode, message: nil)
        }
        
        print("✅ Prediction sent successfully, status: \(httpResponse.statusCode)")
    }
    
    /// Send prediction to BigQuery (callback version - for backward compatibility)
    func sendPredictionCallback(row: PredictionRow, completion: @escaping (Result<Void, Error>) -> Void) {
        guard let url = URL(string: "https://emakiatech-api-b6fc087f7f4f.herokuapp.com/api/prediction") else {
            completion(.failure(APIError.invalidURL))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            let jsonData = try JSONEncoder().encode(row)
            request.httpBody = jsonData
        } catch {
            print("❌ Failed to encode prediction: \(error)")
            completion(.failure(error))
            return
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("❌ Error sending prediction: \(error)")
                completion(.failure(error))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(APIError.invalidResponse))
                return
            }
            
            if httpResponse.statusCode == 200 {
                print("✅ Prediction sent, status: \(httpResponse.statusCode)")
                completion(.success(()))
            } else {
                let errorMessage = data.flatMap { String(data: $0, encoding: .utf8) } ?? "Unknown error"
                print("❌ Prediction failed with status \(httpResponse.statusCode): \(errorMessage)")
                completion(.failure(APIError.serverError(statusCode: httpResponse.statusCode, message: errorMessage)))
            }
        }.resume()
    }
    
    // MARK: - Batch Send Predictions
    
    /// Send multiple predictions efficiently
    func sendPredictionsBatch(_ predictions: [PredictionRow]) async {
        await withTaskGroup(of: Void.self) { group in
            for prediction in predictions {
                group.addTask {
                    do {
                        try await self.sendPrediction(row: prediction)
                    } catch {
                        print("❌ Failed to send prediction for tweet \(prediction.tweet_id): \(error)")
                    }
                }
            }
        }
    }
}

// MARK: - API Error

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case serverError(statusCode: Int, message: String?)
    case decodingError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid API URL"
        case .invalidResponse:
            return "Invalid server response"
        case .serverError(let code, let message):
            if let message = message {
                return "Server error (\(code)): \(message)"
            }
            return "Server error: \(code)"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        }
    }
}

// MARK: - Response Models

struct TweetResponse: Codable {
    let count: Int
    let data: [Tweet]
    let filtersApplied: FiltersApplied?
    
    enum CodingKeys: String, CodingKey {
        case count, data
        case filtersApplied = "filters_applied"
    }
}

struct FiltersApplied: Codable {
    let topic: String?
    let sensitiveFilter: String?
    let limit: Int
    
    enum CodingKeys: String, CodingKey {
        case topic
        case sensitiveFilter = "sensitive_filter"
        case limit
    }
}
