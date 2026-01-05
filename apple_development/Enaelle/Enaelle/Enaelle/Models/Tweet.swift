//
//  Tweet.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//

import Foundation

struct Tweet: Identifiable, Decodable {
    let id: String
    let content: String
    let author_id: String?
    let possibly_sensitive: Bool
    let created_at: String?
    
    // User data from LEFT JOIN - may be null if user not found
    let username: String?
    let name: String?
    let profile_image_url: String?
    
    // Extra fields not in your backend
    let referenced_tweet_id: String?
    let referenced_tweet_type: String?
    let media_url: String?
    let likeCount: Int?
    let retweetCount: Int?
    let replyCount: Int?
    
    enum CodingKeys: String, CodingKey {
        case id = "tweet_id"
        case content
        case author_id
        case possibly_sensitive
        case created_at
        case username
        case name
        case profile_image_url
        case referenced_tweet_id
        case referenced_tweet_type
        case media_url
        case likeCount
        case retweetCount
        case replyCount
    }
}




