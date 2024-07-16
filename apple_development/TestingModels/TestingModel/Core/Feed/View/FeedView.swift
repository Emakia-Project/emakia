//
//  FeedView.swift
//  TestingTableView
//
//  Created by Corinne David on 6/6/23.
//

import SwiftUI

struct FeedView: View {
    @State private var showNewTweetView = false
    @ObservedObject var viewModel = ExploreViewModel()
    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            ScrollView{
                LazyVStack{
                    ForEach(viewModel.tweets, id:\.self){ tweet in
                        TweetRowView(tweet: tweet)
                            .padding()
                    }
                }
            }
            Button {
                showNewTweetView.toggle()
            }
        label: {
                Image("user")
                .resizable()
                .renderingMode(.template)
                .frame(width: 28, height: 28)
                .padding()
            }
        .background(Color(.systemBlue))
        .foregroundColor(.white)
        .clipShape(Circle())
        .padding()
        .fullScreenCover(isPresented: $showNewTweetView){
            Text("New tweet view ")
        }
        }
    }
}

struct FeedView_Previews: PreviewProvider {
    static var previews: some View {
        FeedView()
    }
}
