//
//  TweetCard.swift
//  Enaelle
//
//  Created by Corinne David on 7/19/25.
//

import SwiftUI

// MARK: - Public Figure Registry
// Add any public figure, senator, president, or organization handle here.
// Handles are case-insensitive. Do NOT include the @ symbol.

struct PublicFigureRegistry {
    static let handles: Set<String> = [

        // ── U.S. Presidents & Vice Presidents ──────────────────────
        "potus", "vp", "joebiden", "kamalaharris",
        "realdonaldtrump", "mikepence",

        // ── U.S. Senate ─────────────────────────────────────────────
        "senatedems", "senategop", "senatorcollins",
        "senwarren", "berniesanders",
        "senchuckschumer", "senmcconnell", "sentedcruz",
        "senmarcorubiofla", "senatormenendez", "senatorhassan",
        "senatorshaheen", "senjohnossoff", "senreverendwarnock",
        "senatorromney", "sencorybooker",

        // ── U.S. House ───────────────────────────────────────────────
        "speakerpelosi", "speakerjohnson", "repmtg",
        "aoc", "repilhan", "reptlaib",
        "repjayapal", "housedemocrats", "housegop",

        // ── U.S. Government & Agencies ──────────────────────────────
        "whitehouse", "senategov", "housegov",
        "scotus", "doj", "fbi", "cia",
        "statedept", "usdoj", "secdef", "pentagon",
        "cdc", "fda", "nih", "niaid",
        "epa", "federalreserve", "irs", "usps",
        "ustreasury", "nasa", "noaa",

        // ── International Leaders & Orgs ─────────────────────────────
        "elysee", "10downingst",
        "narendramodi", "justintrudeau",
        "emmanuelmacron", "rishi_sunak",
        "vonderleyen", "un", "antonioguterres",
        "claudiasheinbaum",

        // ── News Organizations ───────────────────────────────────────
        "cnn", "msnbc", "foxnews", "nytimes",
        "washingtonpost", "thehill", "politico",
        "axios", "reuters", "apnews", "bbc",
        "guardian", "npr", "pbs", "cbsnews",
        "abcnews", "nbcnews", "usatoday",
        "wsj", "bloomberg", "theatlantic",
        "huffpost", "vox", "propublica",

        // ── Political Organizations ──────────────────────────────────
        "dccc", "dscc", "dnc", "rnc",
        "nrcc", "nrsc", "moveon",
        "aclu", "aclunational", "naacp",
        "humanrightscampaign", "plannedparenthood",

        // ── Tech Companies & CEOs ────────────────────────────────────
        "elonmusk", "sundarpichai", "satyanadella",
        "tim_cook", "meta", "google", "apple",
        "microsoft", "amazon", "netflix",
        "twitter", "x", "openai", "anthropic",

        // ── Add more handles here as needed ─────────────────────────
    ]

    /// Returns true if the handle is a known public figure or organization
    static func isPublic(_ handle: String) -> Bool {
        let clean = handle
            .lowercased()
            .trimmingCharacters(in: .whitespaces)
            .trimmingCharacters(in: CharacterSet(charactersIn: "@"))
        return handles.contains(clean)
    }
}

// MARK: - String extension: redact @mentions unless public figure

extension String {
    /// Replaces unknown @handles with a grey overlay.
    /// Known public figures and organizations are left visible.
    func redactingMentions() -> AttributedString {
        var attributed = AttributedString(self)
        let regex = try? NSRegularExpression(pattern: "@[A-Za-z0-9_]+")
        let matches = regex?.matches(
            in: self,
            range: NSRange(self.startIndex..., in: self)
        ) ?? []

        for match in matches.reversed() {
            let nsRange = match.range
            guard let swiftRange = Range(nsRange, in: self),
                  let attrRange = Range(swiftRange, in: attributed) else { continue }

            // Extract the handle without @
            let handle = String(String(self[swiftRange]).dropFirst())

            if !PublicFigureRegistry.isPublic(handle) {
                // Private user — grey out
                attributed[attrRange].foregroundColor = .clear
                attributed[attrRange].backgroundColor = .gray.opacity(0.4)
            }
            // Public figure — leave untouched
        }
        return attributed
    }
}

// MARK: - Redacted pill

private struct RedactedPill: View {
    var width: CGFloat = 90
    var height: CGFloat = 14

    var body: some View {
        RoundedRectangle(cornerRadius: 4)
            .fill(Color.gray.opacity(0.35))
            .frame(width: width, height: height)
    }
}

// MARK: - TweetCard

struct TweetCard: View {
    let tweet: Tweet

    private var authorIsPublic: Bool {
        PublicFigureRegistry.isPublic(tweet.username ?? "")
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {

            // 🖼️ Profile & author block
            HStack(alignment: .top, spacing: 12) {

                // Avatar
                if authorIsPublic, let urlStr = tweet.profile_image_url,
                   let url = URL(string: urlStr) {
                    // Public figure — show real avatar
                    AsyncImage(url: url) { image in
                        image.resizable()
                    } placeholder: {
                        Color.gray.opacity(0.2)
                    }
                    .frame(width: 48, height: 48)
                    .clipShape(Circle())
                } else {
                    // Private user — grey circle placeholder
                    Circle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: 48, height: 48)
                        .overlay(
                            Image(systemName: "person.fill")
                                .foregroundColor(.gray.opacity(0.5))
                        )
                }

                VStack(alignment: .leading, spacing: 6) {
                    if authorIsPublic {
                        // Public figure — show real name and handle
                        Text(tweet.name ?? "Unknown")
                            .font(.system(size: 16, weight: .semibold))

                        Text("@\(tweet.username ?? "unknown") • \(tweet.created_at ?? "")")
                            .font(.caption)
                            .foregroundColor(.gray)
                    } else {
                        // Private user — grey pills instead of name/handle
                        RedactedPill(width: 90, height: 14)
                        RedactedPill(width: 70, height: 11)
                    }
                }

                Spacer()

                // Warning triangle for flagged tweets
                if tweet.possibly_sensitive {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.red)
                }
            }

            // 📝 Tweet text — private @mentions redacted, public ones visible
            Text(tweet.content.redactingMentions())
                .font(.body)
                .lineLimit(nil)

            // 📸 Embedded media
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

            // 🔗 Referenced tweet — show type only, never the ID
            if let refType = tweet.referenced_tweet_type {
                Text("🔗 Refers to \(refType.capitalized) tweet")
                    .font(.caption2)
                    .foregroundColor(.blue)
            }

            // 📊 Interaction counts
            HStack(spacing: 24) {
                Label("\(tweet.likeCount ?? 0)",    systemImage: "heart")
                Label("\(tweet.retweetCount ?? 0)", systemImage: "arrow.2.squarepath")
                Label("\(tweet.replyCount ?? 0)",   systemImage: "bubble.left")
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
