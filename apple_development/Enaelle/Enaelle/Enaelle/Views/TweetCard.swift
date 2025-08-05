//
//  TweetCard.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//


import SwiftUI

struct TweetCard: View {
    let tweet: Tweet

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // 🖼️ Profile & author block
            HStack(alignment: .top, spacing: 12) {
                AsyncImage(url: URL(string: tweet.profile_image_url ?? "")) { image in
                    image.resizable()
                } placeholder: {
                    Color.gray.opacity(0.2)
                }
                .frame(width: 48, height: 48)
                .clipShape(Circle())

                VStack(alignment: .leading, spacing: 4) {
                    Text(tweet.name ?? "Unknown")
                        .font(.system(size: 16, weight: .semibold))

                    Text("@\(tweet.username ?? "unknown") • \(tweet.created_at ?? "")")
                        .font(.caption)
                        .foregroundColor(.gray)
                }

                Spacer()
            }

            // 📝 Tweet text
            Text(tweet.content)
                .font(.body)
                .lineLimit(nil)

            // 📸 Embedded media (if available)
            if let mediaURL = tweet.media_url, let url = URL(string: mediaURL) {
                AsyncImage(url: url) { image in
                    image.resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(maxHeight: 240)
                        .clipped()
                        .cornerRadius(12)
                } placeholder: {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 200)
                }
            }

            // 🚨 Sensitive content flag
            if tweet.possibly_sensitive {
                Text("⚠️ Sensitive content")
                    .font(.caption2)
                    .foregroundColor(.red)
            }

            // 🔗 Referenced tweet info
            if let refID = tweet.referenced_tweet_id,
               let refType = tweet.referenced_tweet_type {
                Text("🔗 Refers to \(refType.capitalized) tweet (ID: \(refID))")
                    .font(.caption2)
                    .foregroundColor(.blue)
            }

            // 📊 Interaction metadata
            HStack(spacing: 24) {
                Label("\(tweet.likeCount ?? 0)", systemImage: "heart")
                Label("\(tweet.retweetCount ?? 0)", systemImage: "arrow.2.squarepath")
                Label("\(tweet.replyCount ?? 0)", systemImage: "bubble.left")
            }
            .font(.caption)
            .foregroundColor(.gray)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(16)
        .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
        .padding(.horizontal)
    }
}


/*import SwiftUI

struct TweetCard: View {
    let tweet: Tweet

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 🖼️ User identity section
            HStack(alignment: .top, spacing: 12) {
                AsyncImage(url: URL(string: tweet.profile_image_url ?? "")) { image in
                    image.resizable()
                } placeholder: {
                    ProgressView()
                }
                .frame(width: 48, height: 48)
                .clipShape(Circle())

                VStack(alignment: .leading, spacing: 2) {
                    Text(tweet.name ?? "Unknown Name")
                        .font(.headline)

                    Text("@\(tweet.username ?? "unknown")")
                        .font(.subheadline)
                        .foregroundColor(.gray)

                    if let date = tweet.created_at {
                        Text(date)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()
            }

            // 📝 Tweet content
            Text(tweet.content)
                .font(.body)

            // 🚨 Sensitivity flag
            if tweet.possibly_sensitive {
                Text("⚠️ Sensitive content")
                    .font(.caption2)
                    .foregroundColor(.red)
            }

            // 🔗 Referenced tweet metadata
            if let refID = tweet.referenced_tweet_id,
               let refType = tweet.referenced_tweet_type {
                HStack {
                    Text("🔗 Refers to tweet ID: \(refID)")
                        .font(.caption2)
                        .foregroundColor(.blue)
                    Spacer()
                    Text("Type: \(refType)")
                        .font(.caption2)
                        .foregroundColor(.purple)
                }
            }
        }
        .padding()
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(.systemGray6)))
        .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.gray.opacity(0.3)))
        .shadow(radius: 1)
    }
}*/
