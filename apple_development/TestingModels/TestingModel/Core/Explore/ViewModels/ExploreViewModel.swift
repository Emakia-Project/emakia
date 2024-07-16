//
//  ExploreViewModel.swift
//  TestingModel
//
//  Created by Corinne David on 7/13/23.
//

import Foundation
class ExploreViewModel: ObservableObject {
    @Published var tweets = [Tweet]()
    @Published var neutralTweets = [Tweet]()
    @Published var harassingTweets: [Tweet] = []
    @Published var query = ""
    let service = TweetService()
    
    func fetchTweets(query: String){
        service.setQuery(query: query)
         service.getdata(){ neutralTweets, harassingTweets in
            self.neutralTweets = neutralTweets
            self.harassingTweets = harassingTweets
        }
    }

    func setQuery(query: String){
        self.query = query
        
    }
    
}
