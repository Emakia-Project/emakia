//
//  TweetsRowView.swift
//  TestingTableView
//
//  Created by Corinne David on 6/6/23.
//

import SwiftUI


struct TweetRowView: View {
    //@EnvironmentObject var authViewModel: AuthViewModel
    let tweet: Tweet
    var body: some View {
        
        VStack(alignment: .leading){
            HStack(alignment: .top,spacing:12){
                Circle()
                    .frame(width:56, height:56)
                    .foregroundColor(Color(.systemBlue))
                    .offset(x:6)
                    .overlay(
                        AsyncImage(url: URL(string: tweet.profile_image_url)) { image in
                            image.resizable()
                        } placeholder: {
                            Color.clear
                        }
                        .clipShape(Circle()) // Use Circle shape for circular display
                                
                        )

                //user info & tweet caption
                VStack(alignment: .leading, spacing: 4 ){
                    HStack{
                        Text(tweet.username)
                            .font(.subheadline).bold()
                        Text("@EmakiaTech")
                            .foregroundColor(.gray)
                            .font(.caption)
                        Text("2w")
                            .foregroundColor(.gray)
                            .font(.caption)
                    }
                    // tweet caption
                    Text(tweet.text)
                        .font(.subheadline)
                        .foregroundColor(.black)
                        .multilineTextAlignment(.leading)
                        .padding()
                }
            }
            // action button
            
            HStack{
                Button{
                    // action here
                }label: {
                    Image(systemName: "bubble.left")
                        .font(.subheadline)
                }
                Spacer()
                Button{
                    // action here
                }label: {
                    Image(systemName: "arrow.2.squarepath")
                        .font(.subheadline)
                }
                Spacer()
                Button{
                    // action here
                }label: {
                    Image(systemName: "heart")
                        .font(.subheadline)
                }
                Spacer()
                Button{
                    // action here
                }label: {
                    Image(systemName: "bookmark")
                        .font(.subheadline)
                }
            }
            .padding()
            .foregroundColor(.gray)
            
            Divider()
        }
    }
}

/*struct TweetsRowView_Previews: PreviewProvider {
    static var previews: some View {
        TweetRowView(tweet)
    }
} */
