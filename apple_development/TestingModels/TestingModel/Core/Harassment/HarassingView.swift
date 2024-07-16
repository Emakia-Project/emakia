//
//  harassmentView.swift
//  TestingTableView
//
//  Created by Corinne David on 6/6/23.
//


import SwiftUI

struct HarassingView: View {
    @ObservedObject var viewModel: ExploreViewModel

    var body: some View {
        List(viewModel.harassingTweets) { tweet in
            TweetRowView(tweet: tweet)
        }
        .listStyle(PlainListStyle())
        .navigationTitle("Harassing Tweets")
    }
}

