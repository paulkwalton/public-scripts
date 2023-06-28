using System;
using System.Net;
using System.Net.Sockets;
using System.IO;
using System.Net.Http;

class Program
{
    static void Main()
    {
        // Define start and end IPs for the scan
        string startIP = "192.168.0.1";
        string endIP = "192.168.0.254";

        // Define start and end Ports for the scan
        int startPort = 1;
        int endPort = 1024;

        // Define the output file for the scan results
        string outputFile = "output.txt";

        // Define the test URL for HTTP request
        string testURL = "http://thisisafakesiteandnotinuse.com";

        // Start a new stream writer to write the results to the output file
        using (StreamWriter sw = new StreamWriter(outputFile))
        {
            // Loop over each port in the range
            for (int i = startPort; i <= endPort; i++)
            {
                // Loop over each IP in the range
                for (int j = Convert.ToInt32(startIP.Split('.')[3]); j <= Convert.ToInt32(endIP.Split('.')[3]); j++)
                {
                    // Construct the current IP
                    string currentIP = "192.168.0." + j.ToString();
                    try
                    {
                        // Try to open a TCP connection to the current IP and port
                        TcpClient client = new TcpClient(currentIP, i);

                        // If successful, write to the output file and console
                        sw.WriteLine("Port " + i + " OPEN on " + currentIP);
                        Console.WriteLine("Port " + i + " OPEN on " + currentIP);
                    }
                    catch (Exception)
                    {
                        // If not successful, write to the output file
                        sw.WriteLine("Port " + i + " CLOSED on " + currentIP);
                    }
                }
            }
        }

        // After scanning, try to make an HTTP request to the test URL
        try
        {
            HttpClient client = new HttpClient();
            HttpResponseMessage response = client.GetAsync(testURL).Result;

            // If successful, write the response to the console
            Console.WriteLine("Response from " + testURL + ": " + response.StatusCode);
        }
        catch (Exception e)
        {
            // If not successful, write the error message to the console
            Console.WriteLine("Error connecting to " + testURL + ": " + e.Message);
        }
    }
}

