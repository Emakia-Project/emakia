//
//  TweetView.swift
//  TestingTableView
//
//  Created by Corinne David on 5/19/23.
//

import SwiftUI
import CoreData

struct TweetListView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @FetchRequest(
        sortDescriptors: [NSSortDescriptor(keyPath: \Item.id, ascending: true)],
        animation: .default)
    private var items: FetchedResults<Item>

    var body: some View {
        NavigationView {
            List {
                ForEach(items) { item in
                    NavigationLink {
                        Text("Item at \(item.created_at!, formatter: itemFormatter)")
                    } label: {
                        Text(item.created_at!, formatter: itemFormatter)
                    }
                }
                
                .onDelete(perform: deleteItems)
            }
            
        }
    }

  

    private func deleteItems(offsets: IndexSet) {
        withAnimation {
            offsets.map { items[$0] }.forEach(viewContext.delete)

            do {
                try viewContext.save()
            } catch {
                // Replace this implementation with code to handle the error appropriately.
                // fatalError() causes the application to generate a crash log and terminate. You should not use this function in a shipping application, although it may be useful during development.
                let nsError = error as NSError
                fatalError("Unresolved error \(nsError), \(nsError.userInfo)")
            }
        }
    }
}

private let itemFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .short
    formatter.timeStyle = .medium
    return formatter
}()

/*struct TweetListView_Previews: PreviewProvider {
    static var previews: some View {
        TweetListView()
        ().environment(\.managedObjectContext, PersistenceController.preview.container.viewContext)
    }
}*/
