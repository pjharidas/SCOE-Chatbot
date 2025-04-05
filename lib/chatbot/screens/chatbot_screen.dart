import 'dart:developer';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sgce_college_predictor/chatbot/models/chat.dart';
import 'package:sgce_college_predictor/chatbot/providers/demo_provider.dart';
import 'package:sgce_college_predictor/chatbot/services/demo_service.dart';
import 'package:sgce_college_predictor/chatbot/widgets/chat_bubble.dart';

class ChatbotScreen extends ConsumerWidget {
  const ChatbotScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ChatMessagesProvider chatMessagesPro =
        ref.read(chatMessagesProvider.notifier);
    final List<Chat> chatMessages = ref.watch(chatMessagesProvider);
    final TextEditingController chatBoxCtrl = TextEditingController();
    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: AppBar(
        elevation: 5,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(bottom: Radius.circular(20)),
        ),
        title: const Text(
          'Chatbot',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
        ),
        centerTitle: true,
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.deepPurple, Colors.purpleAccent],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.white, Colors.blueGrey],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: ListView.builder(
                  reverse: false,
                  shrinkWrap: true,
                  itemCount: chatMessages.length,
                  itemBuilder: (context, index) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: ChatBubble(
                        isBot: chatMessages[index].type == ChatterType.bot,
                        message: chatMessages[index].message,
                      ),
                    );
                  },
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 5),
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
                    ].map((suggestion) => Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 8),
                          child: ActionChip(
                            label: Text(suggestion,
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.w500)),
                            backgroundColor: Colors.deepPurpleAccent,
                            onPressed: () {
                              chatBoxCtrl.text = suggestion;
                            },
                          ),
                        )),
                  ],
                ),
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Expanded(
                  flex: 6,
                  child: TextField(
                    controller: chatBoxCtrl,
                    onSubmitted: (value) {
                      submitChat(chatMessagesPro, chatBoxCtrl);
                    },
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                          vertical: 15, horizontal: 20),
                      hintText: 'Type your message here',
                      hintStyle:
                          const TextStyle(color: Colors.grey, fontSize: 16),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  flex: 1,
                  child: Container(
                    height: 50,
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
                        submitChat(chatMessagesPro, chatBoxCtrl);
                      },
                    ),
                  ),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }

  void submitChat(ChatMessagesProvider chatMessagesPro,
      TextEditingController chatBoxCtrl) async {
    log("Adding the message to the chat");
    chatMessagesPro.addMessage(Chat(
      message: chatBoxCtrl.text,
      type: ChatterType.user,
    ));
    String response = await getResponse(chatBoxCtrl.text);
    Chat reply = Chat(
      message: response,
      type: ChatterType.bot,
    );
    chatMessagesPro.addMessage(reply);
    chatBoxCtrl.clear();
  }
}
