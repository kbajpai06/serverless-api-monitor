import urllib.request
import time
import boto3
import json

# Initialize the CloudWatch client
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    api_url = "https://catfact.ninja/fact"
    
    # 1. Start the timer
    start_time = time.time()
    
    try:
        # 2. Ping the API
        req = urllib.request.Request(api_url, headers={'User-Agent': 'AWS-Lambda-Monitor'})
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            
    except Exception as e:
        # If it fails (e.g., timeout or 500 error)
        status_code = 500
        print(f"Error pinging API: {e}")
        
    # 3. Stop the timer and calculate milliseconds
    latency = int((time.time() - start_time) * 1000)
    
    # 4. Determine Uptime (1 for UP, 0 for DOWN)
    is_up = 1 if status_code == 200 else 0
    
    print(f"API Check: Status={status_code}, Latency={latency}ms, Up={is_up}")
    
    # 5. Push the metrics to CloudWatch
    cloudwatch.put_metric_data(
        Namespace='MyProjects/APIMonitor',
        MetricData=[
            {
                'MetricName': 'Uptime',
                'Value': is_up,
                'Unit': 'Count'
            },
            {
                'MetricName': 'ResponseLatency',
                'Value': latency,
                'Unit': 'Milliseconds'
            }
        ]
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Check complete! Latency: {latency}ms')
    }