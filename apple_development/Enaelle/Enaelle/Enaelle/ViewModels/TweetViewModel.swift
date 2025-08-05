//
//  TweetViewModel.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//


//  TweetViewModel.swift
//  Enaelle

import Foundation
import SwiftUI

@MainActor
class TweetViewModel: ObservableObject {
    @Published var tweets: [Tweet] = []

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
        } catch {
            print("❌ Error fetching data:", error)
        }
    }
}



