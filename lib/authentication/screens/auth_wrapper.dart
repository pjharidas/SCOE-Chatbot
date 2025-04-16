import 'package:flutter/material.dart';
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

  // Controllers and form for sign-up/sign-in
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isSignUp = true;
  String? _registeredPassword;

  @override
  void initState() {
    super.initState();
    // Set up the controller for a 2-second animation
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    // Fade animation for the left pane
    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );

    // Slide animation for the right image
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

  void _submit() {
    if (_formKey.currentState!.validate()) {
      final email = _emailController.text;
      final password = _passwordController.text;

      if (_isSignUp) {
        // "Sign-up": store the password in memory.
        _registeredPassword = password;
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Registration Successful'),
            content: Text('Account registered for $email'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => ChatbotScreen()),
          ),
                child: const Text('OK'),
              )
            ],
          ),
        );
      } else {
        // "Sign-in": check the password against the registered one.
        if (_registeredPassword == null) {
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Error'),
              content: const Text('No account found. Please sign up first.'),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('OK'),
                )
              ],
            ),
          );
        } // Inside the _submit() method, replace the "Login Successful" case as follows:
        else if (password == _registeredPassword) {
          // Instead of showing a dialog, navigate to the chatbot screen.
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => ChatbotScreen()),
          );
        } else {
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Authentication Failed'),
              content: const Text('Incorrect password.'),
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
  }

  @override
  Widget build(BuildContext context) {
    // Choose colors based on the current mode.
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
                      // Inline sign-up/sign-in UI
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
                                  validator: (val) =>
                                      (val == null || val.isEmpty)
                                          ? 'Enter an email'
                                          : null,
                                ),
                                const SizedBox(height: 10),
                                TextFormField(
                                  controller: _passwordController,
                                  decoration: const InputDecoration(
                                    labelText: 'Password',
                                    border: OutlineInputBorder(),
                                  ),
                                  obscureText: true,
                                  validator: (val) =>
                                      (val == null || val.isEmpty)
                                          ? 'Enter a password'
                                          : null,
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
                                    child: Text(headerText),
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
              child: Image.asset(
                'assets/images/sgce_building.png',
                height: MediaQuery.of(context).size.height * 0.8,
                fit: BoxFit.cover,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
