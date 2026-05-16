//
//  Tweet.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//


import Foundation

struct Tweet: Identifiable, Codable {  // Changed from Decodable to Codable
    let id: String
    let name: String?
    let username: String?
    let profile_image_url: String?
    let created_at: String?
    let content: String
    let possibly_sensitive: Bool
    let referenced_tweet_id: String?
    let referenced_tweet_type: String?
    let media_url: String?
    let likeCount: Int?
    let retweetCount: Int?
    let replyCount: Int?
    
    // Add these computed properties for convenience
    var authorId: String {
        return username ?? "unknown"
    }
    
    var possiblySensitive: Bool {
        return possibly_sensitive
    }
    
    var createdAtDate: Date? {
        guard let created_at = created_at else { return nil }
        let formatter = ISO8601DateFormatter()
        return formatter.date(from: created_at)
    }
    
    enum CodingKeys: String, CodingKey {
        case id = "tweet_id"
        case name
        case username
        case profile_image_url
        case created_at
        case content
        case possibly_sensitive
        case referenced_tweet_id
        case referenced_tweet_type
        case media_url
        case likeCount
        case retweetCount
        case replyCount
    }
}
