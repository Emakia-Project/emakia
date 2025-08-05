//
//  ContentView.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//



import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = TweetViewModel()
    @State private var selectedPlatform: SocialPlatform = .twitter
    @State private var searchTopic = ""
    @State private var resultLimit = 50
    @State private var showSensitiveOnly = false
    @State private var tabSelection = 0

    var body: some View {
        NavigationView {
            VStack {
                Picker("Platform", selection: $selectedPlatform) {
                    ForEach(SocialPlatform.allCases, id: \.self) { platform in
                        Text(platform.label).tag(platform)
                    }
                }
                .pickerStyle(SegmentedPickerStyle())
                .padding(.horizontal)

                HStack {
                    TextField("Search Topic", text: $searchTopic)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    Stepper("Limit: \(resultLimit)", value: $resultLimit, in: 10...500)
                }.padding()

                Toggle("Show Sensitive Only", isOn: $showSensitiveOnly)
                    .padding(.horizontal)

                Button("Fetch Data") {
                    Task {
                        await viewModel.fetch(
                            from: selectedPlatform,
                            topic: searchTopic,
                            limit: resultLimit,
                            sensitiveFilter: showSensitiveOnly ? true : nil
                        )
                    }
                }
                .buttonStyle(.borderedProminent)
                .padding(.bottom)

                TabView(selection: $tabSelection) {
                    List(viewModel.tweets) { tweet in
                        TweetCard(tweet: tweet)
                    }
                    .tabItem {
                        Label("All Tweets", systemImage: "bubble.left.and.bubble.right")
                    }.tag(0)

                    List(viewModel.tweets.filter { $0.possibly_sensitive }) { tweet in
                        TweetCard(tweet: tweet)
                    }
                    .tabItem {
                        Label("Sensitive", systemImage: "exclamationmark.triangle")
                    }.tag(1)

                    Text("CoreML Toxicity View (Coming Soon)")
                        .tabItem {
                            Label("Toxicity", systemImage: "flame")
                        }.tag(2)
                }
            }
            .frame(minWidth: 0, maxWidth: .infinity) // optional layout fix
            .navigationTitle("Emakia Rebuttal App")
        }
    }
}

#Preview {
    ContentView()
}
