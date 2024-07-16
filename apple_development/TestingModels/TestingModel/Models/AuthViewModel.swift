//
//  AuthViewModel.swift
//  TestingTableView
//
//  Created by Corinne David on 6/12/23.
//

import SwiftUI
import TwitterAPIKit
import Foundation

class AuthViewModel: ObservableObject{
    
    @Published var tweets = [Tweet]()
    private var service = TweetService()
    @Published var query = String()
    init() {
        
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return}
            //print("query from authview")
            //print(self.query)
            self.service.getdata(){
             neutralTweets, harassingTweets in
                //print("tweets")
            }
            
        }
            
        }
    }
    
   
