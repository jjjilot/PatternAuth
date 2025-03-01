//
//  ContentView.swift
//  PatternAuth
//
//  Created by Josh on 2/28/25.
//

import SwiftUI
import SwiftData

import SwiftUI

struct LoginView: View {
    @State private var username = ""
    @State private var password = ""
    @State private var isLoggedIn = false  // Change state on successful login
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Login")
                    .font(.largeTitle)
                    .padding(.bottom, 20)
                
                TextField("Username", text: $username)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .autocapitalization(.none)
                    .padding(.horizontal)
                
                SecureField("Password", text: $password)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.horizontal)
                
                Button(action: {
                    // Here is where you send the credentials to your server or auth service.
                    // For example: authenticate(username: username, password: password)
                    // On successful authentication, update the state to navigate to the main app.
                    isLoggedIn = true
                }) {
                    Text("Sign In")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
                .padding(.horizontal)
                
                NavigationLink(
                    destination: MainView(),  // Replace MainView() with your app's main screen
                    isActive: $isLoggedIn,
                    label: { EmptyView() }
                )
            }
            .padding()
            .navigationBarHidden(true)
        }
    }
}

struct MainView: View {
    var body: some View {
        Text("Welcome to the App!")
            .font(.title)
    }
}

struct LoginView_Previews: PreviewProvider {
    static var previews: some View {
        LoginView()
    }
}
