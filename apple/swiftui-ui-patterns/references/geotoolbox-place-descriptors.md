# Place Descriptors (GeoToolbox + MapKit)

## Overview
Use this reference when working with PlaceDescriptor and GeoToolbox interop with MapKit.

## Create PlaceDescriptor
```swift
import GeoToolbox

let fountain = PlaceDescriptor(
    representations: [.address("121-122 James's St \n Dublin 8 \n D08 ET27 \n Ireland")],
    commonName: "Obelisk Fountain"
)
```

```swift
let eiffelTower = PlaceDescriptor(
    representations: [.coordinate(CLLocationCoordinate2D(latitude: 48.8584, longitude: 2.2945))],
    commonName: "Eiffel Tower"
)
```

## From MKMapItem
```swift
import MapKit
import GeoToolbox

func convertMapItemToDescriptor(mapItem: MKMapItem) -> PlaceDescriptor? {
    PlaceDescriptor(item: mapItem)
}
```

## Service identifiers
```swift
let landmark = PlaceDescriptor(
    representations: [.address("1 Infinite Loop, Cupertino, CA 95014")],
    commonName: "Apple Park",
    supportingRepresentations: [
        .serviceIdentifiers([
            "com.apple.maps": "ABC123XYZ",
            "com.google.maps": "ChIJq6qq6jK1j4ARzl-WRHNx9CI"
        ])
    ]
)
```

## Geocoding
```swift
func geocodeAddress(address: String) async throws -> [MKMapItem] {
    guard let request = MKGeocodingRequest(addressString: address) else {
        throw NSError(domain: "GeocodingError", code: 1, userInfo: nil)
    }
    return try await request.mapItems
}
```

```swift
func reverseGeocode(coordinate: CLLocationCoordinate2D) async throws -> [MKMapItem] {
    let location = CLLocation(latitude: coordinate.latitude, longitude: coordinate.longitude)
    guard let request = MKReverseGeocodingRequest(location: location) else {
        throw NSError(domain: "ReverseGeocodingError", code: 1, userInfo: nil)
    }
    return try await request.mapItems
}
```

## References
- https://developer.apple.com/documentation/GeoToolbox
- https://developer.apple.com/documentation/GeoToolbox/PlaceDescriptor
- https://developer.apple.com/documentation/MapKit
- https://developer.apple.com/documentation/MapKit/MKMapItem
- https://developer.apple.com/documentation/MapKit/MKGeocodingRequest
- https://developer.apple.com/documentation/MapKit/MKReverseGeocodingRequest
