//
//  Tweet.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//


import Foundation



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

    // Add this line
    let media_url: String?
    
    // Optional metadata
    let likeCount: Int?
    let retweetCount: Int?
    let replyCount: Int?
}



