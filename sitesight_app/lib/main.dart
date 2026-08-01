import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

// TODO: Replace with your actual Supabase credentials
const String supabaseUrl = 'YOUR_SUPABASE_URL';
const String supabaseAnonKey = 'YOUR_SUPABASE_ANON_KEY';

void main() async {
  // Ensure Flutter bindings are initialized before using async code
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Supabase
  await Supabase.initialize(
  url: supabaseUrl,
  publishableKey: supabaseAnonKey,
);

  runApp(const SiteSightApp());
}

class SiteSightApp extends StatelessWidget {
  const SiteSightApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SiteSight IoT',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const ViolationsDashboard(),
    );
  }
}

class ViolationsDashboard extends StatefulWidget {
  const ViolationsDashboard({super.key});

  @override
  State<ViolationsDashboard> createState() => _ViolationsDashboardState();
}

class _ViolationsDashboardState extends State<ViolationsDashboard> {
  final _supabase = Supabase.instance.client;
  List<Map<String, dynamic>> _violations = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchViolations();
  }

  Future<void> _fetchViolations() async {
  setState(() => _isLoading = true);
  try {
    debugPrint('Fetching from Supabase...');
    debugPrint('URL: $supabaseUrl');
    
    final response = await _supabase
        .from('violations')
        .select()
        .order('created_at', ascending: false);
    
    debugPrint('Response: $response');
    
    setState(() {
      _violations = List<Map<String, dynamic>>.from(response);
      _isLoading = false;
    });
  } catch (e, stackTrace) {
    debugPrint(' Error: $e');
    debugPrint('Stack: $stackTrace');
    setState(() => _isLoading = false);
  }
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SiteSight Dashboard'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _fetchViolations,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _violations.isEmpty
              ? const Center(child: Text('No violations recorded yet.'))
              : ListView.builder(
                  itemCount: _violations.length,
                  itemBuilder: (context, index) {
                    final violation = _violations[index];
                    final ipfsCid = violation['ipfs_cid'] as String;
                    final txHash = violation['tx_hash'] as String;
                    final vType = violation['violation_type'] as String;
                    final createdAt = violation['created_at'] as String;
                    
                    // Format the timestamp
                    final dateTime = DateTime.parse(createdAt);
                    final formattedTime = DateFormat('MMM dd, yyyy - HH:mm').format(dateTime);

                    // Construct IPFS Gateway URL
                    final imageUrl = 'https://gateway.pinata.cloud/ipfs/$ipfsCid';
                    final explorerUrl = 'https://etherscan.io/tx/$txHash'; // Or your local explorer if preferred

                    return Card(
                      margin: const EdgeInsets.all(8.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // IPFS Image
                          ClipRRect(
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                            child: CachedNetworkImage(
                              imageUrl: imageUrl,
                              height: 200,
                              width: double.infinity,
                              fit: BoxFit.cover,
                              placeholder: (context, url) => const Center(child: CircularProgressIndicator()),
                              errorWidget: (context, url, error) => const Icon(Icons.error),
                            ),
                          ),
                          Padding(
                            padding: const EdgeInsets.all(12.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      vType.toUpperCase().replaceAll('_', ' '),
                                      style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.redAccent,
                                      ),
                                    ),
                                    Text(
                                      formattedTime,
                                      style: TextStyle(color: Colors.grey[600], fontSize: 12),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Row(
                                  children: [
                                    const Icon(Icons.link, size: 16, color: Colors.blue),
                                    const SizedBox(width: 4),
                                    Expanded(
                                      child: Text(
                                        'TX: ${txHash.substring(0, 10)}...${txHash.substring(txHash.length - 8)}',
                                        style: const TextStyle(fontSize: 12, color: Colors.blue),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                ElevatedButton.icon(
                                  onPressed: () async {
                                    final uri = Uri.parse(explorerUrl);
                                    if (await canLaunchUrl(uri)) {
                                      await launchUrl(uri, mode: LaunchMode.externalApplication);
                                    }
                                  },
                                  icon: const Icon(Icons.verified, size: 18),
                                  label: const Text('Verify on Blockchain'),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.green,
                                    foregroundColor: Colors.white,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}