//
//  Tweet.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//


import Foundation


/*struct Tweet: Codable, Identifiable {
    let id: String               // maps to tweet_id
    let content: String
    let author_id: String
    let created_at: String?
    let possibly_sensitive: Bool
    let referenced_tweet_id: String?
    let referenced_tweet_type: String?
    let name: String?                    // display name
    let username: String?                // handle like @user
    let profile_image_url: String?       // avatar URL

    enum CodingKeys: String, CodingKey {
        case id = "tweet_id"
        case content
        case author_id
        case created_at
        case possibly_sensitive
        case referenced_tweet_id
        case referenced_tweet_type
        case name
        case username
        case profile_image_url
    }
}*/
struct Tweet: Identifiable {
    let id: String
    let name: String?
    let username: String?
    let profile_image_url: String?
    let created_at: String?
    let content: String
    let possibly_sensitive: Bool
    let referenced_tweet_id: String?
    let referenced_tweet_type: String?

    // ✅ Add this line
    let media_url: String?
    
    // Optional metadata
    let likeCount: Int?
    let retweetCount: Int?
    let replyCount: Int?
}



