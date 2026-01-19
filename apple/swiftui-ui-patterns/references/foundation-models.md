# Foundation Models (Apple Intelligence)

## Overview
Use this reference when integrating Apple's on-device Foundation Models and LanguageModelSession APIs.

## Availability check
```swift
struct GenerativeView: View {
    private var model = SystemLanguageModel.default

    var body: some View {
        switch model.availability {
        case .available:
            Text("Model is available")
        case .unavailable(.deviceNotEligible):
            Text("Device not eligible for Apple Intelligence")
        case .unavailable(.appleIntelligenceNotEnabled):
            Text("Please enable Apple Intelligence in Settings")
        case .unavailable(.modelNotReady):
            Text("Model is downloading or not ready")
        case .unavailable(let other):
            Text("Model unavailable: \(other)")
        }
    }
}
```

## Session and instructions
```swift
let instructions = """
You are a helpful assistant that provides concise answers.
Keep responses under 100 words and focus on clarity.
"""

let session = LanguageModelSession(instructions: instructions)
```

## Respond to prompts
```swift
let response = try await session.respond(to: "What's a good month to visit Paris?")
print(response.content)
```

## Guided generation
```swift
@Generable
struct CatProfile {
    var name: String

    @Guide(description: "The age of the cat", .range(0...20))
    var age: Int

    @Guide(description: "A one sentence profile about the cat's personality")
    var profile: String
}

let response = try await session.respond(
    to: "Generate a cute rescue cat",
    generating: CatProfile.self
)
print(response.content.name)
```

## Tool calling
```swift
struct RecipeSearchTool: Tool {
    struct Arguments: Codable {
        var searchTerm: String
        var numberOfResults: Int
    }

    func call(arguments: Arguments) async throws -> ToolOutput {
        let recipes = await searchRecipes(term: arguments.searchTerm, limit: arguments.numberOfResults)
        return .string(recipes.map { "- \($0.name): \($0.description)" }.joined(separator: "\n"))
    }
}

let session = LanguageModelSession(tools: [RecipeSearchTool()])
let answer = try await session.respond(to: "Find me some pasta recipes")
```

## Snapshot streaming
```swift
@Generable
struct TripIdeas {
    @Guide(description: "Ideas for upcoming trips")
    var ideas: [String]
}

let stream = session.streamResponse(
    to: "What are some exciting trip ideas for the upcoming year?",
    generating: TripIdeas.self
)

for try await partial in stream {
    print(partial)
}
```

## References
- https://developer.apple.com/documentation/FoundationModels/generating-content-and-performing-tasks-with-foundation-models
- https://developer.apple.com/documentation/FoundationModels/generating-swift-data-structures-with-guided-generation
- https://developer.apple.com/documentation/FoundationModels/expanding-generation-with-tool-calling
- https://developer.apple.com/design/human-interface-guidelines/technologies/generative-ai
