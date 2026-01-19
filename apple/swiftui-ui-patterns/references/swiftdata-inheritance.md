# SwiftData Class Inheritance

## Overview
Use this reference when modeling SwiftData class hierarchies or querying polymorphic models.

## Base class
```swift
import SwiftData

@Model class Trip {
    @Attribute(.preserveValueOnDeletion)
    var name: String
    var destination: String

    @Attribute(.preserveValueOnDeletion)
    var startDate: Date

    @Attribute(.preserveValueOnDeletion)
    var endDate: Date

    @Relationship(deleteRule: .cascade, inverse: \Accommodation.trip)
    var accommodation: Accommodation?

    init(name: String, destination: String, startDate: Date, endDate: Date) {
        self.name = name
        self.destination = destination
        self.startDate = startDate
        self.endDate = endDate
    }
}
```

## Subclasses
```swift
@Model class BusinessTrip: Trip {
    var purpose: String
    var expenseCode: String
    var perDiemRate: Double

    @Relationship(deleteRule: .cascade, inverse: \BusinessMeal.trip)
    var businessMeals: [BusinessMeal] = []

    init(name: String, destination: String, startDate: Date, endDate: Date,
         purpose: String, expenseCode: String, perDiemRate: Double) {
        self.purpose = purpose
        self.expenseCode = expenseCode
        self.perDiemRate = perDiemRate
        super.init(name: name, destination: destination, startDate: startDate, endDate: endDate)
    }
}
```

```swift
@Model class PersonalTrip: Trip {
    enum Reason: String, CaseIterable, Codable, Identifiable {
        case family, vacation, wellness, other
        var id: Self { self }
    }

    var reason: Reason
    var notes: String?

    init(name: String, destination: String, startDate: Date, endDate: Date,
         reason: Reason, notes: String? = nil) {
        self.reason = reason
        self.notes = notes
        super.init(name: name, destination: destination, startDate: startDate, endDate: endDate)
    }
}
```

## Querying by type
```swift
let businessTripPredicate = #Predicate<Trip> { $0 is BusinessTrip }
@Query(filter: businessTripPredicate)
var businessTrips: [Trip]
```

## Best practices
- Keep hierarchies shallow.
- Prefer inheritance only for true IS-A relationships.
- Consider enum or composition when only a few fields differ.

## References
- https://developer.apple.com/documentation/SwiftData/Adopting-inheritance-in-SwiftData
