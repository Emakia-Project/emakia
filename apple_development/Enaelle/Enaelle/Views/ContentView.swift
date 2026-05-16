
//
//  ContentView.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//
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
                .padding(.bottom, 8)
                
                // Model selector
                if !viewModel.allModelResults.isEmpty {
                    VStack(spacing: 4) {
                        Text("Model Version:")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        Picker("Model", selection: $viewModel.selectedModel) {
                            ForEach(ModelVersion.allCases, id: \.self) { version in
                                Text(version.displayName).tag(version)
                            }
                        }
                        .pickerStyle(SegmentedPickerStyle())
                        .padding(.horizontal)
                        .onChange(of: viewModel.selectedModel) { _ in
                            viewModel.updateDisplayForSelectedModel()
                        }
                    }
                    .padding(.bottom, 8)
                }
                
                // Classification progress indicator
                if viewModel.isClassifying {
                    HStack {
                        ProgressView()
                        Text("Classifying with 3 models...")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .padding(.bottom, 8)
                }

                TabView(selection: $tabSelection) {
                    // All Tweets Tab
                    VStack {
                        HStack {
                            Text("Total: \(viewModel.tweets.count)")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Spacer()
                            if !viewModel.allModelResults.isEmpty {
                                Text("Viewing: \(viewModel.selectedModel.displayName)")
                                    .font(.caption)
                                    .foregroundColor(.blue)
                            }
                        }
                        .padding(.horizontal)
                        
                        if viewModel.tweets.isEmpty {
                            VStack {
                                Image(systemName: "bubble.left.and.bubble.right")
                                    .font(.system(size: 48))
                                    .foregroundColor(.gray)
                                Text("No tweets loaded")
                                    .font(.headline)
                                    .padding(.top)
                                Text("Search for a topic to get started")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                        } else {
                            List(viewModel.tweets) { tweet in
                                VStack(alignment: .leading, spacing: 8) {
                                    TweetCard(tweet: tweet)
                                    
                                    // Show predictions from all models
                                    if let modelResults = viewModel.allModelResults[tweet.id] {
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text("Model Predictions:")
                                                .font(.caption2)
                                                .foregroundColor(.gray)
                                            
                                            ForEach(ModelVersion.allCases, id: \.self) { version in
                                                if let result = modelResults[version] {
                                                    HStack {
                                                        Circle()
                                                            .fill(result.isHarassment ? Color.red : Color.green)
                                                            .frame(width: 6, height: 6)
                                                        Text("\(version.rawValue): \(result.category) (\(result.confidencePercentage)%)")
                                                            .font(.caption2)
                                                            .foregroundColor(.gray)
                                                    }
                                                }
                                            }
                                        }
                                        .padding(.horizontal)
                                        .padding(.vertical, 4)
                                        .background(Color.gray.opacity(0.1))
                                        .cornerRadius(4)
                                    }
                                }
                                .overlay(alignment: .topTrailing) {
                                    if let result = viewModel.toxicityResults[tweet.id] {
                                        if result.isHarassment {
                                            Image(systemName: "exclamationmark.triangle.fill")
                                                .foregroundColor(.red)
                                                .padding(8)
                                        }
                                    }
                                }
                            }
                        }
                    }
                    .tabItem {
                        Label("All Tweets", systemImage: "bubble.left.and.bubble.right")
                    }
                    .tag(0)
                    .badge(viewModel.tweets.count)

                    // Neutral Tab
                    VStack {
                        HStack {
                            Text("Neutral: \(viewModel.neutralTweets.count)")
                                .font(.caption)
                                .foregroundColor(.green)
                            Spacer()
                        }
                        .padding(.horizontal)
                        
                        if viewModel.neutralTweets.isEmpty {
                            VStack {
                                Image(systemName: "checkmark.circle")
                                    .font(.system(size: 48))
                                    .foregroundColor(.green)
                                Text("No neutral tweets found")
                                    .font(.headline)
                                    .padding(.top)
                                Text("Fetch tweets to see neutral content")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                        } else {
                            List(viewModel.neutralTweets) { tweet in
                                VStack(alignment: .leading, spacing: 8) {
                                    TweetCard(tweet: tweet)
                                    
                                    if let result = viewModel.toxicityResults[tweet.id] {
                                        HStack {
                                            Image(systemName: "checkmark.circle.fill")
                                                .foregroundColor(.green)
                                            Text("Neutral • Confidence: \(result.confidencePercentage)%")
                                                .font(.caption)
                                                .foregroundColor(.gray)
                                        }
                                        .padding(.horizontal)
                                        .padding(.bottom, 4)
                                    }
                                }
                            }
                            .listStyle(.plain)
                        }
                    }
                    .tabItem {
                        Label("Neutral", systemImage: "checkmark.circle")
                    }
                    .tag(1)
                    .badge(viewModel.neutralTweets.count)

                    // Harassment Tab (Toxicity)
                    VStack {
                        HStack {
                            Text("Harassment: \(viewModel.harassmentTweets.count)")
                                .font(.caption)
                                .foregroundColor(.red)
                            Spacer()
                        }
                        .padding(.horizontal)
                        
                        if viewModel.harassmentTweets.isEmpty {
                            VStack {
                                Image(systemName: "checkmark.shield")
                                    .font(.system(size: 48))
                                    .foregroundColor(.green)
                                Text("No harassment detected")
                                    .font(.headline)
                                    .padding(.top)
                                Text("All tweets are classified as neutral")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                        } else {
                            List(viewModel.harassmentTweets) { tweet in
                                VStack(alignment: .leading, spacing: 8) {
                                    TweetCard(tweet: tweet)
                                    
                                    if let result = viewModel.toxicityResults[tweet.id] {
                                        HStack {
                                            Image(systemName: "flame.fill")
                                                .foregroundColor(.red)
                                            Text("Harassment • Confidence: \(result.confidencePercentage)%")
                                                .font(.caption)
                                                .foregroundColor(.red)
                                        }
                                        .padding(.horizontal)
                                        .padding(.bottom, 4)
                                    }
                                }
                            }
                            .listStyle(.plain)
                        }
                    }
                    .tabItem {
                        Label("Toxic", systemImage: "flame")
                    }
                    .tag(2)
                    .badge(viewModel.harassmentTweets.count)
                }
            }
            .frame(minWidth: 0, maxWidth: .infinity)
            .navigationTitle("Emakia Rebuttal App")
        }
    }
}

#Preview {
    ContentView()
}
