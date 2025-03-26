import 'package:flutter/material.dart';
import 'package:sgce_college_predictor/chatbot/screens/chatbot_screen.dart';

class AuthenticationWrapper extends StatelessWidget {
  const AuthenticationWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    String email = '';
    String password = '';
    return Scaffold(
      body: Row(
        // direction: Axis.horizontal,
        // alignment: WrapAlignment.center,
        spacing: 10,
        children: [
          Flexible(
              child: Container(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              spacing: 10,
              children: [
                Image.asset('assets/images/logo.png'),
                const Text(
                  'Welcome to SCOE College Predictor',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                SizedBox(
                  width: 300,
                  child: TextField(
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      labelText: 'Email',
                      hintText: 'Enter your email',
                    ),
                    onChanged: (value) {
                      email = value;
                    },
                  ),
                ),
                SizedBox(
                  width: 300,
                  child: TextField(
                    obscureText: true,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      labelText: 'Password',
                      hintText: 'Enter your password',
                    ),
                    onChanged: (value) {
                      password = value;
                    },
                  ),
                ),
                ElevatedButton(
                  onPressed: () {
                    print('Email: $email, Password: $password');
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const ChatbotScreen()));
                  },
                  child: const Text('Login'),
                ),
                TextButton(
                  onPressed: () {
                    print('Forgot password');
                  },
                  child: const Text('Forgot password?'),
                ),
              ],
            ),
          )),
          Flexible(
              flex: 2,
              child: Column(
                children: [
                  Image.asset(
                    'assets/images/sgce_building.png',
                    height: MediaQuery.of(context).size.height * 0.8,
                  ),
                ],
              )),
        ],
      ),
    );
  }
}
