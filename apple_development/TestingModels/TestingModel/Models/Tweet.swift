//
//  Tweet.swift
//  TestingTableView
//
//  Created by Corinne David on 7/4/23.
//

import Foundation


struct TweetsArrayReponse: Codable {
  
        var tweetsArray: [Tweet]?

}
    
 

struct Tweet: Codable, Hashable, Identifiable{
    
    let id: String
    let edit_history_tweet_ids: [String]
    let text: String
    let author_id: String
    let username: String
    let profile_image_url: String
}
