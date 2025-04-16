import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:sgce_college_predictor/authentication/services/firebase.dart';
import 'package:sgce_college_predictor/chatbot/screens/chatbot_screen.dart';

class AuthenticationWrapper extends StatefulWidget {
  const AuthenticationWrapper({super.key});

  @override
  State<AuthenticationWrapper> createState() => _AuthenticationWrapperState();
}

class _AuthenticationWrapperState extends State<AuthenticationWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  final _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isSignUp = true;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.2),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _toggleAuthMode() {
    setState(() {
      _isSignUp = !_isSignUp;
    });
  }

  Future<void> _submit() async {
    if (_formKey.currentState!.validate()) {
      final email = _emailController.text.trim();
      final password = _passwordController.text.trim();

      try {
        AuthService authService = AuthService();
        if (_isSignUp) {
          // Call method in firebase.dart to create a new user.
          final User? user = await authService.register(email, password,context);
          if (user != null) {
            showDialog(
              context: context,
              builder: (context) => AlertDialog(
                title: const Text('Registration Successful'),
                content: Text('Account registered for $email'),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const ChatbotScreen()),
                    ),
                    child: const Text('OK'),
                  )
                ],
              ),
            );
          } 
        }
        else{
          // Call method in firebase.dart to sign in the user.
          final User? user = await authService.signIn(email, password, context);
          if (user != null) {
            showDialog(
              context: context,
              builder: (context) => AlertDialog(
                title: const Text('Login Successful'),
                content: Text('Welcome back, $email!'),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const ChatbotScreen()),
                    ),
                    child: const Text('OK'),
                  )
                ],
              ),
            );
          }
        }
      } catch (e) {
        // Display error dialog if authentication fails.
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Authentication Failed'),
            content: Text(e.toString()),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('OK'),
              )
            ],
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color primaryColor = _isSignUp ? Colors.green : Colors.blue;
    final String headerText = _isSignUp ? 'Create Account' : 'Login';
    final String toggleText = _isSignUp
        ? 'Already have an account? Login'
        : 'Don\'t have an account? Create Account';

    return Scaffold(
      body: Row(
        children: [
          Flexible(
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: Container(
                padding: const EdgeInsets.all(20),
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Image.asset('assets/images/logo.png'),
                      const SizedBox(height: 20),
                      const Text(
                        'Welcome to SCOE College Predictor',
                        style: TextStyle(
                            fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 20),
                      Card(
                        elevation: 4,
                        color: _isSignUp ? Colors.green[50] : Colors.blue[50],
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Form(
                            key: _formKey,
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  headerText,
                                  style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: primaryColor),
                                ),
                                const SizedBox(height: 16),
                                TextFormField(
                                  controller: _emailController,
                                  decoration: const InputDecoration(
                                    labelText: 'Email',
                                    border: OutlineInputBorder(),
                                  ),
                                  validator: (val) {
                                    if (val == null || val.isEmpty) {
                                      return 'Enter an email';
                                    }
                                    // Basic email validation
                                    final emailRegex =
                                        RegExp(r'^[^@]+@[^@]+\.[^@]+');
                                    if (!emailRegex.hasMatch(val)) {
                                      return 'Enter a valid email';
                                    }
                                    return null;
                                  },
                                ),
                                const SizedBox(height: 10),
                                TextFormField(
                                  controller: _passwordController,
                                  decoration: const InputDecoration(
                                    labelText: 'Password',
                                    border: OutlineInputBorder(),
                                  ),
                                  obscureText: true,
                                  validator: (val) {
                                    if (val == null || val.isEmpty) {
                                      return 'Enter a password';
                                    }
                                    if (val.length < 6) {
                                      return 'Password must be at least 6 characters';
                                    }
                                    return null;
                                  },
                                ),
                                const SizedBox(height: 20),
                                SizedBox(
                                  width: double.infinity,
                                  child: ElevatedButton(
                                    onPressed: _submit,
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: primaryColor,
                                      padding: const EdgeInsets.symmetric(
                                          vertical: 14),
                                      textStyle: const TextStyle(fontSize: 16),
                                    ),
                                    child: Text(headerText, style: TextStyle(color: Colors.white),),
                                  ),
                                ),
                                const SizedBox(height: 10),
                                TextButton(
                                  onPressed: _toggleAuthMode,
                                  child: Text(toggleText),
                                )
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
            Flexible(
            flex: 2,
            child: SlideTransition(
              position: _slideAnimation,
              child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                const Text(
                  'Meet your College Assistant Chatbot!',
                  style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 20),
                // Network GIF animation resembling a chatbot interaction.
                Image.network(
                  'https://media.giphy.com/media/3o72FCZylk0zYUaFi0/giphy.gif',
                  height: MediaQuery.of(context).size.height * 0.5,
                  fit: BoxFit.cover,
                ),
                ],
              ),
              ),
            ),
            ),
          
        ],
      ),
    );
  }
}
