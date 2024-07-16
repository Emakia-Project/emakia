//
//  ExploreView.swift
//  TestingTableView
//
//  Created by Corinne David on 6/6/23.
//

import SwiftUI

struct ExploreView: View {
    @ObservedObject var viewModel: ExploreViewModel
    @State var text = ""

    var body: some View {
        VStack {
            // Search bar
            HStack {
                TextField("Search...", text: $text)
                    .padding(8)
                    .padding(.horizontal, 24)
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                    .overlay(
                        HStack {
                            Image(systemName: "magnifyingglass")
                                .foregroundColor(.gray)
                                .frame(minWidth: 0, maxWidth: .infinity, alignment: .leading)
                                .padding(.leading, 8)
                        }
                    )
                    .onSubmit {
                        if text.isEmpty { return }
                        viewModel.fetchTweets(query: text)
                    }
                    .padding(.horizontal, 4)
                    .submitLabel(.search)
            }

            // Neutral Tweets List
           // print("viewModel.neutralTweets.capacity")
           // print(viewModel.neutralTweets.capacity)
            List(viewModel.neutralTweets) { tweet in
                TweetRowView(tweet: tweet)
            }
            .listStyle(PlainListStyle())
            .navigationTitle("Neutral Tweets")
        }
        .task(id: text) {
            if text.isEmpty {
                return
            }
        }
    }
}
