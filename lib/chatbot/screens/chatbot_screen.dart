import 'dart:developer';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sgce_college_predictor/authentication/screens/auth_wrapper.dart';
import 'package:sgce_college_predictor/chatbot/models/chat.dart';
import 'package:sgce_college_predictor/chatbot/providers/demo_provider.dart';
import 'package:sgce_college_predictor/chatbot/services/demo_service.dart';
import 'package:sgce_college_predictor/chatbot/widgets/chat_bubble.dart';

// Convert to ConsumerStatefulWidget
class ChatbotScreen extends ConsumerStatefulWidget {
  const ChatbotScreen({super.key});

  @override
  ConsumerState<ChatbotScreen> createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends ConsumerState<ChatbotScreen> {
  // Create controllers
  final TextEditingController _chatBoxCtrl = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    // Dispose controllers
    _chatBoxCtrl.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // Function to scroll to the bottom
  void _scrollToBottom() {
    // Use addPostFrameCallback to scroll after the frame is built
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final ChatMessagesProvider chatMessagesPro =
        ref.read(chatMessagesProvider.notifier);
    // Watch the provider and scroll when it changes
    final List<Chat> chatMessages = ref.watch(chatMessagesProvider);

    // Use ref.listen to react to state changes for scrolling
    ref.listen<List<Chat>>(chatMessagesProvider, (_, __) {
      _scrollToBottom();
    });
    User? currentUser = FirebaseAuth.instance.currentUser;

    return Scaffold(
      backgroundColor: Colors.grey[200],
      bottomNavigationBar: Container(
        height: 20,
        decoration: BoxDecoration(
          color: Colors.black,
          boxShadow: const [
            BoxShadow(
              color: Colors.black26,
              blurRadius: 4,
              offset: Offset(0, -2),
            ),
          ],
        ),
        child: Text(
          currentUser?.email?.toString() ??
              'guest' + ": " + (currentUser?.uid?.toString() ?? ''),
          style: TextStyle(color: Colors.white),
        ),
      ),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        title: const Text(
          'College Predictor and assistant Chatbot',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            tooltip: "Logout",
            icon: const Icon(Icons.logout, color: Colors.black),
            onPressed: () async {
              await FirebaseAuth.instance.signOut();
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                  builder: (context) => const AuthenticationWrapper(),
                ),
              );
            },
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              // No Align needed if ListView is not reversed
              child: ListView.builder(
                // Attach scroll controller
                controller: _scrollController,
                // reverse: false, // Keep false for natural top-to-bottom order
                // shrinkWrap: true, // Avoid shrinkWrap with Expanded
                itemCount: chatMessages.length,
                itemBuilder: (context, index) {
                  String fullMessage = chatMessages[index].message;
                  int indexOfBioTech =
                      fullMessage.indexOf("Biotechnology Intake") - 1;
                  int indexOfFee = fullMessage.indexOf("Fee (Open)") - 1;
                  int indexOfAddDocs =
                      fullMessage.indexOf("Admission Documents Required:") - 1;
                  int indexOfClubs = fullMessage.indexOf("Clubs:") - 1;
                  int indexOfCulturalAct =
                      fullMessage.indexOf("Cultural Activities:") - 1;
                  Widget child = chatMessages[index].message.length > 900
                      ? Column(
                          children: [
                            ChatBubble(
                              onEdit: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                              },
                              onRegenerate: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                                submitChat(chatMessagesPro, _chatBoxCtrl);
                              },
                              isBot:
                                  chatMessages[index].type == ChatterType.bot,
                              message: chatMessages[index]
                                  .message
                                  .substring(0, indexOfBioTech),
                            ),
                            ChatBubble(
                              onEdit: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                              },
                              onRegenerate: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                                submitChat(chatMessagesPro, _chatBoxCtrl);
                              },
                              isBot:
                                  chatMessages[index].type == ChatterType.bot,
                              message: chatMessages[index]
                                  .message
                                  .substring(indexOfBioTech, indexOfFee),
                            ),
                            ChatBubble(
                              onEdit: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                              },
                              onRegenerate: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                                submitChat(chatMessagesPro, _chatBoxCtrl);
                              },
                              isBot:
                                  chatMessages[index].type == ChatterType.bot,
                              message: chatMessages[index]
                                  .message
                                  .substring(indexOfFee, indexOfAddDocs),
                            ),
                            ChatBubble(
                              onEdit: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                              },
                              onRegenerate: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                                submitChat(chatMessagesPro, _chatBoxCtrl);
                              },
                              isBot:
                                  chatMessages[index].type == ChatterType.bot,
                              message: chatMessages[index]
                                  .message
                                  .substring(indexOfAddDocs, indexOfClubs),
                            ),
                            ChatBubble(
                              onEdit: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                              },
                              onRegenerate: () {
                                _chatBoxCtrl.text = chatMessages[index].message;
                                submitChat(chatMessagesPro, _chatBoxCtrl);
                              },
                              isBot:
                                  chatMessages[index].type == ChatterType.bot,
                              message: chatMessages[index]
                                  .message
                                  .substring(indexOfClubs, indexOfCulturalAct),
                            )
                          ],
                        )
                      : ChatBubble(
                          onEdit: () {
                            _chatBoxCtrl.text = chatMessages[index].message;
                          },
                          onRegenerate: () {
                            _chatBoxCtrl.text = chatMessages[index].message;
                            submitChat(chatMessagesPro, _chatBoxCtrl);
                          },
                          isBot: chatMessages[index].type == ChatterType.bot,
                          message: chatMessages[index].message,
                        );
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: child,
                  );
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(
                  bottom: 5, top: 10), // Added top padding
              child: SizedBox(
                height: 50,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  children: [
                    ...[
                      'List all colleges',
                      'What college can I get with 90 percentile if my category is OPEN',
                      'Give me information about Sinhgad College of Engineering',
                      'Give me contact details of SMT. Kashibai Navale College Of Engineering',
                      "What college can I get with 90 percentile if my category is OPEN for IT branch"
                    ].map((suggestion) => Padding(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 4), // Reduced horizontal padding
                          child: ActionChip(
                            shadowColor: Colors.deepPurple,
                            elevation: 5,
                            label: Text(suggestion,
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.w500)),
                            backgroundColor: Colors.deepPurpleAccent,
                            onPressed: () {
                              _chatBoxCtrl.text = suggestion;
                              // Optionally submit immediately after suggestion click
                              // submitChat(chatMessagesPro, _chatBoxCtrl);
                            },
                          ),
                        )),
                  ],
                ),
              ),
            ),
            Padding(
              // Wrap Row in Padding for spacing
              padding: const EdgeInsets.only(top: 5.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Expanded(
                    flex: 6,
                    child: TextField(
                      // Use the state's controller
                      controller: _chatBoxCtrl,
                      onSubmitted: (value) {
                        submitChat(chatMessagesPro, _chatBoxCtrl);
                      },
                      decoration: InputDecoration(
                        filled: true,
                        fillColor: Colors.grey[100], // Lighter fill color
                        contentPadding: const EdgeInsets.symmetric(
                            vertical: 15, horizontal: 20),
                        hintText: 'Type your message here',
                        hintStyle: const TextStyle(
                            fontSize: 16, color: Colors.grey), // Hint style
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(30),
                          borderSide: BorderSide.none, // Remove border
                        ),
                        enabledBorder: OutlineInputBorder(
                          // Border when enabled but not focused
                          borderRadius: BorderRadius.circular(30),
                          borderSide: BorderSide.none,
                        ),
                        focusedBorder: OutlineInputBorder(
                          // Border when focused
                          borderRadius: BorderRadius.circular(30),
                          borderSide: BorderSide(
                              color: Colors.deepPurple,
                              width: 1.5), // Highlight focus
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    flex: 1,
                    child: Container(
                      height: 50, // Match TextField height
                      decoration: BoxDecoration(
                        color: Colors.deepPurple,
                        borderRadius: BorderRadius.circular(25),
                        boxShadow: const [
                          BoxShadow(
                            color: Colors.black26,
                            blurRadius: 4,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                      child: IconButton(
                        icon: const Icon(
                          Icons.send,
                          color: Colors.white,
                        ),
                        onPressed: () {
                          submitChat(chatMessagesPro, _chatBoxCtrl);
                        },
                      ),
                    ),
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  // Move submitChat inside the state
  void submitChat(ChatMessagesProvider chatMessagesPro,
      TextEditingController chatBoxCtrl) async {
    final text = chatBoxCtrl.text.trim(); // Trim whitespace
    if (text.isEmpty) return; // Don't send empty messages

    log("Adding the message to the chat");
    // Add user message
    chatMessagesPro.addMessage(Chat(
      message: text,
      type: ChatterType.user,
    ));
    // Clear input *before* waiting for response
    chatBoxCtrl.clear();
    // Scroll after adding user message (optional, ref.listen handles it too)
    // _scrollToBottom();

    // Get bot response
    String response = await getResponse(text);
    Chat reply = Chat(
      message: response,
      type: ChatterType.bot,
    );
    // Add bot message
    chatMessagesPro.addMessage(reply);
    // Scrolling is handled by ref.listen
  }
}
