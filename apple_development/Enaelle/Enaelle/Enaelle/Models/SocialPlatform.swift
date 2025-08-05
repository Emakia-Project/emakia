//
//  SocialPlatform.swift
//  Enaelle
//
//  Created by Corinne David on 7/22/25.
//

//  SocialPlatform.swift
//  Enaelle

enum SocialPlatform: String, CaseIterable {
    case twitter, reddit, facebook

    var apiEndpoint: String {
        switch self {
        case .twitter:
            return "https://emakiatech-api-b6fc087f7f4f.herokuapp.com/api/tweet-cascade"
        case .reddit:
            return "https://emakiatech-api.herokuapp.com/api/reddit-cascade"
        case .facebook:
            return "https://emakiatech-api.herokuapp.com/api/facebook-cascade"
        }
    }

    var label: String {
        self.rawValue.capitalized
    }
}
