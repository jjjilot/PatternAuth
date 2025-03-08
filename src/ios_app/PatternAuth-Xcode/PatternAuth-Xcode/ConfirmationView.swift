import SwiftUI

struct ConfirmationView: View {
    let pattern: [Int]

    var body: some View {
        VStack {
            Spacer() // Pushes everything down

            Text("Pattern Set Successfully!")
                .font(.largeTitle)
                .padding(.top)

            Text("Your Pattern Key: \(pattern.map(String.init).joined(separator: " → "))")
                .font(.headline)
                .padding()

            // Grid Diagram
            VStack(spacing: 10) {
                ForEach(0..<3, id: \.self) { row in
                    HStack(spacing: 10) {
                        ForEach(0..<3, id: \.self) { col in
                            let index = row * 3 + col
                            Text("\(index)")
                                .frame(width: 50, height: 50)
                                .background(Color.gray.opacity(0.2))
                                .cornerRadius(25)
                        }
                    }
                }
            }
            .padding()

            Spacer() // Pushes everything up
        }
        .padding()
        .frame(maxHeight: .infinity) // Ensures it takes up all available space
    }
}

struct ConfirmationView_Previews: PreviewProvider {
    static var previews: some View {
        ConfirmationView(pattern: [0, 1, 2, 4, 7])
    }
}
