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
      appBar: AppBar(
        title: const Text('Chatbot'),
        centerTitle: true,
        backgroundColor: Colors.grey[500],
        elevation: 2,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          spacing: 30,
          // reverse: true,
          children: [
            Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: ListView.builder(
                  shrinkWrap: true,
                  itemCount: chatMessages.length,
                  itemBuilder: (context, index) {
                    return ChatBubble(
                      isBot: chatMessages[index].type == ChatterType.bot,
                      message: chatMessages[index].message,
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
                      'What college can i get with 90 percentile if my category is OPEN',
                      'Give me information about Sinhgad College of Engineering',
                      'Give me contact details of SMT. Kashibai Navale College Of Engineering',
                    ].map((suggestion) => Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 8),
                          child: ActionChip(
                            label: Text(suggestion),
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
                SizedBox(
                  width: MediaQuery.of(context).size.width * 0.60,
                  child: TextField(
                    controller: chatBoxCtrl,
                    onSubmitted: (value) {
                      submitChat(chatMessagesPro, chatBoxCtrl);
                    },
                    enableInteractiveSelection: true,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.all(Radius.circular(30)),
                      ),
                      hintText: 'Type your message here',
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () {
                    submitChat(chatMessagesPro, chatBoxCtrl);
                  },
                  icon: const Icon(Icons.send),
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
