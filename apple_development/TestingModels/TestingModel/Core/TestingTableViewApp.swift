//
//  TestingTableViewApp.swift
//  TestingTableView
//
//  Created by Corinne David on 5/19/23.
//

import SwiftUI

@main
struct TestingTableViewApp: App {
    let persistenceController = PersistenceController.shared
  
    @StateObject var viewModel = AuthViewModel()
    var body: some Scene {
        WindowGroup {
            NavigationView{
                ContentView()
                    .environment(\.managedObjectContext, persistenceController.container.viewContext)
                    .environmentObject(viewModel)
            }
        }
    }
}
