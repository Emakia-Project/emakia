//
//  TweetService.swift
//  TestingTableView
//
//  Created by Corinne David on 6/12/23.
//

import Foundation
import TwitterAPIKit
import CoreML
import NaturalLanguage


let string_endpoint = "2023-05-09T1:00:00.00Z"
let dateFormatter = DateFormatter()
let date_endpoint = dateFormatter.date(from: string_endpoint)
let string_beginningpoint = "2023-05-09T1:00:00.00Z"
let date_beginningpoint = dateFormatter.date(from: string_beginningpoint)


// Use the environment variables from Env.swift
let client = TwitterAPIClient(.bearer(Env.barenToken))

var lines: [String] = []
    
class  TweetService{
//completion: @escaping (_ filteredArray: [Int]) -> Void)
    //var query = "Stephen King"
    var query = ""
    
    func setQuery(query: String){
        self.query = query
    
    }
  func getdata(completion: @escaping([Tweet], [Tweet]) ->Void ) {
            
       // var tweets = [Tweet]()
      var neutralTweets = [Tweet]()
      var harassingTweets = [Tweet]()
      
        do{
            
            try?
            client.v2.search.searchTweetsRecent(.init(query: self.query, expansions: TwitterTweetExpansionsV2.all, maxResults: 100,userFields: TwitterUserFieldsV2.all )).responseObject{ [self] response in
                // print(response)
                if (( response.success) != nil) {
                    print("response.data!.count")
                    print(response.data!.count)
                    //tweets = parse(json: response.data!)
                    let (neutralTweets, harassingTweets) = parse(json: response.data!)
                    DispatchQueue.main.async {
                        completion(neutralTweets, harassingTweets)
                    }
                }
                
            }
          
        }

        }

        
    func parse(json: Data) -> (neutralTweets: [Tweet], harassingTweets: [Tweet]) {
        var neutralTweets = [Tweet]()
        var harassingTweets = [Tweet]()
        
        do {
            // Load your Core ML model (replace 'emakiaTweetsSentimentClassifier' with your actual model class)
            guard let mlModel = try? emakiaTweetsSentimentClassifier(configuration: MLModelConfiguration()).model else {
                fatalError("Error loading the model.")
            }
            let sentimentPredictor = try NLModel(mlModel: mlModel)
            let tweet_array = try JSONSerialization.jsonObject(with: json, options: .allowFragments) as! NSDictionary
            
            let ardata = tweet_array["data"] as! [Any]
            var username = ""
            var profile_image_url = ""
            for dd in ardata {
                let d = dd as? [String: Any]
                let txt = d!["text"] as! String
                let id = d!["id"] as! String
                let his = d!["edit_history_tweet_ids"] as! [String]
                let au = d!["author_id"] as! String
                //if let entities = d?["entities"] as? [Any]
                let entities = d?["entities"] as? [String: Any]
                let mentions = entities?["mentions"] as? [Any]
                
                var mention: [String: Any]? = (mentions?.first as? [String: Any])
                username = mention?["username"] as? String ?? ""
                
                if let profile_image_url = d?["profile_image_url"] as? String {
                    print(profile_image_url)
                    // Use the profile_image_url safely
                } else {
                    // Handle the case where the value is nil
                    print(profile_image_url)
                }
                //let profile_image_url = d!["profile_image_url"] as! String
                
                let sentimentPrediction = try sentimentPredictor.predictedLabel(for: txt)
                print(profile_image_url)
                let t = Tweet(id: id, edit_history_tweet_ids: his, text: txt, author_id: au, username: username, profile_image_url: profile_image_url)
                
                if sentimentPrediction == "Neutral" {
                    neutralTweets.append(t)
                } else {
                    harassingTweets.append(t)
                }
            }
            
            return (neutralTweets, harassingTweets)
        } catch {
            print("Error processing tweets: \(error)")
            return ([], []) // Return empty arrays in case of an error
        }
    }
        
    }
    
    
    
    

