//
//  Tweet.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//


import Foundation


struct Tweet: Identifiable, Decodable {
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
    
    enum CodingKeys: String, CodingKey {
        case id = "tweet_id"  // Maps JSON "tweet_id" to Swift "id"
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




