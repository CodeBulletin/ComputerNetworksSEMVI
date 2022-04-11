#include <iostream>
#include <string>
#include <random>
#include <algorithm>
#include <climits>

char XOR(const char& a, const char& b) {
    return a == b ? '0' : '1';
}

std::string binary_modulo(std::string a, const std::string& b) {
    int i = 0;
	for (i = 0; i < a.size() && a[i] != '1'; i++);
	for (; i < a.size() - b.size() + 1; i++) {
		for (int j = 0; j < b.size(); j++) {
			a[i + j] = XOR(a[i + j], b[j]);
		}
		for (; i < a.size() - 1 && a[i + 1] != '1'; i++);
	}
    return a;
}

std::string add_n0s(std::string str, const int& n) {
    for (int i = 0; i < n-1; i++) {
		str += "0";
	}
    return str;
}

std::string generateCRC(std::string binary_message, std::string CRCPolynomial) {
    std::string remainder = binary_modulo(add_n0s(binary_message, CRCPolynomial.size()), CRCPolynomial);
	std::string EndBits = remainder.substr(remainder.size() - CRCPolynomial.size() + 1);
	return binary_message + EndBits;
}

bool checkCRC(std::string binary_message, std::string CRCPolynomial) {
	std::string remainder = binary_modulo(binary_message, CRCPolynomial);
	for (int i = 0; i < remainder.size(); i++) {
		if (remainder[i] != '0') return false;
	}
	return true;
}

std::string Transmit(std::string message, int error_type, int length) {
	if (error_type != 0) {
		std::random_device rd;
		std::mt19937 mte(rd());
		if (error_type == 1) {
			std::vector<size_t> pos;
			for (int i = 0; i < message.size(); i++) {
				pos.push_back(i);
			}
			for (int i = 0; i < std::min<int>(length, message.size()); i++) {
				std::uniform_int_distribution<int> ue(0, pos.size()-1);
				int j = pos[ue(mte)];
				message[j] = message[j] == '1' ? '0' : '1';
				pos.erase(std::find(pos.begin(), pos.end(), j));
			}
		}
		else {
			std::uniform_int_distribution<int> ue(0, message.size() - length);
			int i = ue(mte);
			for (int j = 0; j < length; j++) {
				message[i + j] = message[i + j] == '1' ? '0' : '1';
			}
		}
	}
	return message;
}

int main() {
    std::string message, poly, encoded_message, transmitted_message;
    int error_type = 0, burst_length = 0;
    bool error_detected = false;

    int opt;
    std::string clr = "\033[2J\033[1;1H";

    std::cout << clr;

    bool running = true;
    while (running) {
        std::cout
            << "~~~Main Menu~~~\n"
            << "1. Enter the message to send\n"
            << "2. Enter the Polynomial\n"
            << "3. Transmission Errors settings\n"
            << "4. Show sent and received message\n"
            << "5. Resend message\n"
            << "6. Exit\n"
            << "Enter the choice: ";
        std::cin >> opt;

        switch (opt) {
            case 1:
                std::cout << "Enter the message: ";
                std::cin >> message;
                if(poly.size() > 0) {
                    encoded_message = generateCRC(message, poly);
                    transmitted_message = Transmit(encoded_message, error_type, burst_length);
                    error_detected = !checkCRC(transmitted_message, poly);
                }
                break;
            
            case 2:
                std::cout << "Enter the polynomial: ";
                std::cin >> poly;
                if(message.size() > 0) {
                    encoded_message = generateCRC(message, poly);
                    transmitted_message = Transmit(encoded_message, error_type, burst_length);
                    error_detected = !checkCRC(transmitted_message, poly);
                }
                break;

            case 3:
                std::cout << "Enter the Error Type (0 - no error, 1 - random bits error, 2 - burst error): ";
                std::cin >> error_type;

                std::cout << "Enter the number of bits: ";
                std::cin >> burst_length;

                if(message.size() > 0 && poly.size() > 0) {
                    encoded_message = generateCRC(message, poly);
                    transmitted_message = Transmit(encoded_message, error_type, burst_length);
                    error_detected = !checkCRC(transmitted_message, poly);
                }
                break;
            
            case 4:
                std::cout
                    << clr
                    << "Message(in binary): " << message << "\n"
                    << "Polynomial(in binary): " << poly << "\n"
                    << "Encoded Message(in binary): " << encoded_message << "\n"
                    << "Received Message(in binary): " << transmitted_message << "\n"
                    << "Error detected: " << (error_detected ? "Yes" : "No") << "\n"
                    << "Error Settings: (Error type: " << (error_type == 0 ? "No error" : (error_type == 1 ? "Random bits" : "Burst")) << " | Bits: " << burst_length << ")\n";
                
                std::cin.ignore();
                std::cin.get();
                break;
            
            case 5:
                if(message.size() > 0 && poly.size() > 0) {
                    encoded_message = generateCRC(message, poly);
                    transmitted_message = Transmit(encoded_message, error_type, burst_length);
                    error_detected = !checkCRC(transmitted_message, poly);
                }
                break;
            
            case 6:
                running = false;
                break;
            
            default:
                std::cout << "Wrong Option \n";
                break;
        }
        std::cout << clr;
    }

    return 0; 
}