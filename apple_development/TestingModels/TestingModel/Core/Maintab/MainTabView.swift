//
//  MainTabView.swift
//  TestingTableView
//
//  Created by Corinne David on 6/6/23.
//

import SwiftUI

struct MainTabView: View {
    
    let viewModel = ExploreViewModel() // Declare the viewModel here
    @State private var selectedIndex = 0
    var body: some View {

        TabView(selection: $selectedIndex){
            FeedView()
                .onTapGesture {
                    self.selectedIndex = 0
                }
                .tabItem {
                    Image(systemName: "house")
                }.tag(0)
            
            ExploreView(viewModel: viewModel)
                .onTapGesture {
                    self.selectedIndex = 1
                }
                .tabItem {
                    Image(systemName: "magnifyingglass")
                }.tag(1)
            
            HarassingView(viewModel: viewModel)
                .onTapGesture {
                    self.selectedIndex = 2
                }
                .tabItem {
                    Image(systemName: "shield.slash")
                }.tag(2)
            
            MessageView()
                .onTapGesture {
                    self.selectedIndex = 3
                }
                .tabItem {
                    Image(systemName: "envelope")
                }.tag(3)
        }
    }
}

struct MainTabView_Previews: PreviewProvider {
    static var previews: some View {
        MainTabView()
    }
}
