//
//  Fibackup.swift
//  TestingTableView
//
//  Created by Corinne David on 7/5/23.
//

import Foundation
func getdata()async  {
    var data:Data?
    let decoder = JSONDecoder()
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    do{
       // print( "get data")
        //var i = 0
        try?
        client.v2.search.searchTweetsRecent(.init(query: "Bush")).responseObject{ response in
            data = response.data!
            //return try decoder.decode(T.self, from: response.data? ?? ) as! Void
            do{
                
                let tweet_array = try JSONSerialization.jsonObject(with: data!, options: .allowFragments) as! [String: Any]/*[[String: Any]]*/// [AnyHashable : Any] //[Tweet]
                
                let tt = (tweet_array["data"] ?? [Tweet].self  as Any)
             
            }catch{
                print("error")
                
            }
        }
    }
        
        
        
        
        //return self.tweets!
    }




