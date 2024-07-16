//
//  ContentView.swift
//  TestingTableView
//
//  Created by Corinne David on 6/7/23.
//

import SwiftUI

struct ContentView: View {
    var viewModel = ExploreViewModel()

    var body: some View {
        TabView {
            ExploreView(viewModel: viewModel)
                .tabItem {
                    Label("Neutral", systemImage: "person.fill")
                }

            HarassingView(viewModel: viewModel)
                .tabItem {
                    Label("Harassing", systemImage: "exclamationmark.triangle.fill")
                }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
