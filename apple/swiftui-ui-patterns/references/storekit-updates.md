# StoreKit Updates

## Overview
Use this reference when implementing StoreKit updates for in-app purchases, subscriptions, or StoreKit views.

## AppTransaction updates (iOS 18.4+)
```swift
Task {
    do {
        let appTransaction = try await AppTransaction.shared
        let transactionID = appTransaction.appTransactionID
        let platform = appTransaction.originalPlatform
        if platform == .iOS {
            // iOS-specific logic
        }
    } catch {
        print("Failed to get app transaction: \(error)")
    }
}
```

## Transaction updates
```swift
Task {
    for await verificationResult in Transaction.currentEntitlements(for: "your.product.id") {
        switch verificationResult {
        case .verified(let transaction):
            let appTransactionID = transaction.appTransactionID
            if let offerPeriod = transaction.offerPeriod {
                // handle offer period
            }
        case .unverified(_, let verificationError):
            print("Verification failed: \(verificationError)")
        }
    }
}
```

## RenewalInfo updates
```swift
Task {
    do {
        let status = try await Product.SubscriptionInfo.Status(transactionID: "transaction_id_here")
        if let renewalInfo = status.renewalInfo,
           let expirationReason = renewalInfo.expirationReason {
            switch expirationReason {
            case .priceIncrease:
                break
            case .billingError:
                break
            default:
                break
            }
        }
    } catch {
        print("Failed to get subscription status: \(error)")
    }
}
```

## SubscriptionOfferView
```swift
SubscriptionOfferView(productID: "your.subscription.id")
    .prefersPromotionalIcon(true)
```

```swift
SubscriptionOfferView(productID: "your.subscription.id") {
    Image("custom_icon")
        .resizable()
        .frame(width: 40, height: 40)
} placeholderIcon: {
    Image(systemName: "hourglass")
        .resizable()
        .frame(width: 40, height: 40)
}
```

## subscriptionStatusTask
```swift
.subscriptionStatusTask(for: "your.group.id") { statuses in
    if statuses.contains(where: { $0.state == .subscribed }) {
        customerStatus = .subscribed
    } else if statuses.contains(where: { $0.state == .expired }) {
        customerStatus = .expired
    } else {
        customerStatus = .notSubscribed
    }
}
```

## JWS signing requirement (offers)
Use App Store Server Library for JWS signing (intro offers, promos).

## References
- https://developer.apple.com/documentation/storekit
- https://developer.apple.com/videos/play/wwdc2025/241/
- https://developer.apple.com/documentation/StoreKit/getting-started-with-in-app-purchases-using-storekit-views
- https://developer.apple.com/documentation/StoreKit/understanding-storekit-workflows
- https://github.com/apple/app-store-server-library-swift
