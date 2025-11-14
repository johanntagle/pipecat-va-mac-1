-- Seed data for development and testing

-- Insert sample companies
INSERT INTO companies (name, openai_api_key, system_prompt, llm_model) VALUES
(
  'Acme Corporation',
  'sk-test-acme-key-replace-with-real-key',
  'You are a helpful customer service assistant for Acme Corporation. Be professional, friendly, and concise. Help customers with product inquiries, technical support, and scheduling appointments.',
  'gpt-4o-mini'
),
(
  'TechStart Inc',
  'sk-test-techstart-key-replace-with-real-key',
  'You are an AI assistant for TechStart Inc, a cutting-edge technology company. Provide technical support, answer product questions, and help schedule demos with our sales team.',
  'gpt-4o'
),
(
  'Global Services Ltd',
  'sk-test-global-key-replace-with-real-key',
  'You represent Global Services Ltd. Assist customers with service inquiries, billing questions, and appointment scheduling. Always be courteous and professional.',
  'gpt-3.5-turbo'
);

-- Insert sample calls
INSERT INTO calls (company_id, start_time, end_time, call_summary) VALUES
(
  1,
  NOW() - INTERVAL '2 hours',
  NOW() - INTERVAL '2 hours' + INTERVAL '5 minutes',
  'Customer inquired about product pricing and features. Scheduled a demo for next week.'
),
(
  1,
  NOW() - INTERVAL '1 day',
  NOW() - INTERVAL '1 day' + INTERVAL '3 minutes',
  'Technical support call regarding login issues. Issue resolved by resetting password.'
),
(
  2,
  NOW() - INTERVAL '3 hours',
  NOW() - INTERVAL '3 hours' + INTERVAL '8 minutes',
  'Sales inquiry about enterprise plan. Customer requested detailed pricing information and scheduled follow-up call.'
),
(
  2,
  NOW() - INTERVAL '30 minutes',
  NOW() - INTERVAL '25 minutes',
  'Quick question about API documentation. Directed customer to developer portal.'
),
(
  3,
  NOW() - INTERVAL '5 hours',
  NOW() - INTERVAL '5 hours' + INTERVAL '10 minutes',
  'Billing inquiry about recent invoice. Explained charges and updated payment method.'
);

-- Insert sample call details (conversation logs)
-- Call 1 - Acme Corp pricing inquiry
INSERT INTO call_details (call_id, speaker, timestamp, message) VALUES
(1, 'caller', NOW() - INTERVAL '2 hours', 'Hi, I''m interested in learning more about your products.'),
(1, 'agent', NOW() - INTERVAL '2 hours' + INTERVAL '2 seconds', 'Hello! I''d be happy to help you learn about our products. What specific area are you interested in?'),
(1, 'caller', NOW() - INTERVAL '2 hours' + INTERVAL '8 seconds', 'I''m looking at your enterprise plan. What''s the pricing like?'),
(1, 'agent', NOW() - INTERVAL '2 hours' + INTERVAL '12 seconds', 'Our enterprise plan starts at $999 per month and includes advanced features like priority support, custom integrations, and dedicated account management. Would you like to schedule a demo to see it in action?'),
(1, 'caller', NOW() - INTERVAL '2 hours' + INTERVAL '20 seconds', 'Yes, that would be great. How about next Tuesday?'),
(1, 'agent', NOW() - INTERVAL '2 hours' + INTERVAL '25 seconds', 'Perfect! I can schedule you for next Tuesday at 2 PM. May I have your name and contact number?'),
(1, 'caller', NOW() - INTERVAL '2 hours' + INTERVAL '30 seconds', 'Sure, it''s John Smith, and my number is 555-0123.'),
(1, 'agent', NOW() - INTERVAL '2 hours' + INTERVAL '35 seconds', 'Thank you, John! I''ve scheduled your demo for next Tuesday at 2 PM. You''ll receive a confirmation email shortly. Is there anything else I can help you with?'),
(1, 'caller', NOW() - INTERVAL '2 hours' + INTERVAL '40 seconds', 'No, that''s all. Thank you!'),
(1, 'agent', NOW() - INTERVAL '2 hours' + INTERVAL '42 seconds', 'You''re welcome! Have a great day!');

-- Call 2 - Acme Corp technical support
INSERT INTO call_details (call_id, speaker, timestamp, message) VALUES
(2, 'caller', NOW() - INTERVAL '1 day', 'I can''t log into my account. It says my password is incorrect.'),
(2, 'agent', NOW() - INTERVAL '1 day' + INTERVAL '3 seconds', 'I''m sorry to hear that. I can help you reset your password. Can you confirm your email address?'),
(2, 'caller', NOW() - INTERVAL '1 day' + INTERVAL '8 seconds', 'It''s jane.doe@example.com'),
(2, 'agent', NOW() - INTERVAL '1 day' + INTERVAL '12 seconds', 'Thank you. I''ve sent a password reset link to that email. Please check your inbox and follow the instructions.'),
(2, 'caller', NOW() - INTERVAL '1 day' + INTERVAL '20 seconds', 'Got it, thanks! I see the email now.'),
(2, 'agent', NOW() - INTERVAL '1 day' + INTERVAL '25 seconds', 'Great! Is there anything else I can assist you with today?'),
(2, 'caller', NOW() - INTERVAL '1 day' + INTERVAL '28 seconds', 'No, that''s all. Thanks for your help!');

-- Call 3 - TechStart sales inquiry
INSERT INTO call_details (call_id, speaker, timestamp, message) VALUES
(3, 'caller', NOW() - INTERVAL '3 hours', 'Hi, I''m calling about your enterprise solutions.'),
(3, 'agent', NOW() - INTERVAL '3 hours' + INTERVAL '2 seconds', 'Hello! I''d be happy to discuss our enterprise solutions. What size is your organization?'),
(3, 'caller', NOW() - INTERVAL '3 hours' + INTERVAL '8 seconds', 'We have about 500 employees and we''re looking for a scalable solution.'),
(3, 'agent', NOW() - INTERVAL '3 hours' + INTERVAL '15 seconds', 'Perfect! Our enterprise plan is designed for organizations your size. It includes unlimited users, advanced analytics, and 24/7 support. Would you like me to send you detailed pricing information?'),
(3, 'caller', NOW() - INTERVAL '3 hours' + INTERVAL '25 seconds', 'Yes please, and can we schedule a call to discuss implementation?'),
(3, 'agent', NOW() - INTERVAL '3 hours' + INTERVAL '30 seconds', 'Absolutely! I''ll send the pricing details to your email. For the implementation discussion, would Thursday at 10 AM work for you?'),
(3, 'caller', NOW() - INTERVAL '3 hours' + INTERVAL '38 seconds', 'Thursday at 10 works. My name is Michael Chen, email is m.chen@company.com, phone 555-0456.'),
(3, 'agent', NOW() - INTERVAL '3 hours' + INTERVAL '45 seconds', 'Perfect, Michael! I''ve scheduled our call for Thursday at 10 AM and you''ll receive the pricing details shortly. Looking forward to speaking with you!');

-- Insert sample appointments
INSERT INTO appointments (company_id, call_id, caller_name, caller_contact_number, appointment_details) VALUES
(
  1,
  1,
  'John Smith',
  '555-0123',
  'Product demo scheduled for next Tuesday at 2 PM. Customer interested in enterprise plan features and pricing.'
),
(
  2,
  3,
  'Michael Chen',
  '555-0456',
  'Implementation discussion call scheduled for Thursday at 10 AM. Organization has 500 employees, interested in enterprise solution.'
),
(
  1,
  NULL,
  'Sarah Johnson',
  '555-0789',
  'Follow-up consultation scheduled for Friday at 3 PM. Existing customer looking to upgrade plan.'
);

-- Note: Documents and RAG chunks are not seeded here as they require actual file uploads
-- and embedding generation. These will be created through the application UI.

-- Display summary
DO $$
BEGIN
  RAISE NOTICE 'Seed data inserted successfully!';
  RAISE NOTICE 'Companies: %', (SELECT COUNT(*) FROM companies);
  RAISE NOTICE 'Calls: %', (SELECT COUNT(*) FROM calls);
  RAISE NOTICE 'Call Details: %', (SELECT COUNT(*) FROM call_details);
  RAISE NOTICE 'Appointments: %', (SELECT COUNT(*) FROM appointments);
END $$;

