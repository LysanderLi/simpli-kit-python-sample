# SIMPLI Kit Python Sample

This repository contains Python sample code for working with Acceleronix SIMPLI-Kit hardware, providing a complete solution for IoT sensor data collection and cloud connectivity.

## Project Structure

The project is organized into the following components:

- **Main Application:** Entry point that initializes all services
- **Drivers:** Hardware interfaces for various sensors (SHTC3, LPS22HB, TCS34725, ICM20948)
- **Extensions:** Services for GNSS, LBS, sensors, and Acceleronix cloud connectivity
- **Libraries:** Utility modules for I2C communication, threading, logging, etc.

## Configuration
Please update the `config.json` file with your product credentials created in [Acceleronix IoT Developer Center](https://core.acceleronix.io/).
   ```json
   {
       "QTH_PRODUCT_KEY": "your_product_key",
       "QTH_PRODUCT_SECRET": "your_product_secret",
       "QTH_SERVER": "mqtt://your-server-address:1883"
   }
   ```
## Hardware Components

### Supported Sensors
| Sensor | Description | Capabilities |
|--------|-------------|--------------|
| SHTC3 | Temperature & humidity sensor | High-accuracy environmental monitoring |
| LPS22HB | Barometric pressure sensor | Pressure and temperature readings |
| TCS34725 | RGB color sensor | Color detection and light sensing |
| ICM20948 | 9-axis motion sensor | Accelerometer, gyroscope, and magnetometer |

<img  src="/images/sensor_board.png"  alt="Sensor Board"  width="700px"  height="auto">

### Services
- **GNSS Service:** GPS location tracking and position reporting
- **LBS Service:** Location approximation using cellular tower information
- **Sensor Service:** Collection and aggregation of sensor data
- **Qth Client:** Cloud connectivity and data transmission

## Getting Started

### 1. Get to Know Your SIMPLI-Kit

The SIMPLI-Kit by Acceleronix lets you connect effortlessly to the Acceleronix Asset Management SaaS, enabling quick cloud service demos with zero setup hassle. This guide will walk you through using the SIMPLI-Kit to explore platform features seamlessly.

#### 1.1 What is SIMPLI-Kit?

The SIMPLI-Kit is your gateway to exploring the Acceleronix Asset Management SaaS. Built on the QuecPython **EG912U-GLAA** evaluation board, it’s designed for fast, plug-and-play connectivity.

##### 1.1.1 Compatible Modules
| Product Line | Module |
|--|--|
|LTE Standard | EG912U-GL |

The SIMPLI-Kit supports the following module:  

##### 1.1.2 Unboxing Your SIMPLI-Kit

Here’s what your SIMPLI-Kit looks like out of the box:

<img  src="/images/simpli_kit_top_view.jpg"  alt="SIMPLI-Kit Top View"  width="350px"  height="auto">

##### 1.1.3 What’s Inside the Box?

See the components included in your SIMPLI-Kit package:

<img  src="/images/simpli_kit_unboxing.png"  alt="SIMPLI-Kit Unboxing"  width="500px"  height="auto">

##### 1.1.4 Boards at a Glance

Here’s a look at the boards of the SIMPLI-Kit:

- EG912U-GL QuecPython board:

<img  src="/images/quecpython_board_overview.png"  alt="QuecPython Board Overview"  width="300px"  height="auto">

- Raspberry Pi Sensor HAT B

<img  src="/images/raspberry_pi_sensor_hat_b_board.png"  alt="Raspberry Pi Sensor HAT B Board"  width="300px"  height="auto">

##### 1.1.6 Included Accessories

Your SIMPLI-Kit comes with the following accessories:

<img  src="/images/simpli_kit_accessories.png"  alt="SIMPLI-Kit Accessories"  width="500px"  height="auto">

**Accessories List**

| Item  | Description |  | 
|--|--|-- | 
|USB-C Cable | For powering and connecting the SIMPLI-Kit | 1 |
|USB Memory Stick | 32GB storage with preloaded resources | 1 |
|Welcome Card | Includes quick start instructions | 1 |
|Antenna | YF0028AA Cellular (4G/3G/2G) Antenna | 1 |
|Acrylic Case | Protective case for the SIMPLI-Kit | 1 |
  
### 2. Set Up Your SIMPLI-Kit

Let’s get started! Follow these steps to power up your SIMPLI-Kit:


1. Connect the SIMPLI-Kit to your laptop or a power bank using the provided USB-C cable.

2. The device will power on, automatically connect to the internet via vSIM, and link to the Acceleronix Asset Management SaaS.

<img  src="/images/power_device_on.jpg"  alt="Power the device on"  width="350px"  height="auto">

>**Note**: The SIMPLI-Kit automatically enables vSIM and includes a 20MB/month data plan for 6 months for testing purposes.

### 3. Connect to the Asset Management SaaS

The Asset Management SaaS platform, developed by Acceleronix, offers a comprehensive solution for specialized industries. It covers the entire business process from TSL model feature definition to SaaS platform management and mobile app device control.

This Asset Management SaaS platform enables device operation for users, allowing dynamic analysis of hardware data based on the TSL model. It integrates various sensors, such as water quality, temperature, humidity, light, and carbon dioxide, to suit different scenarios. Features include real-time data viewing, historical operating curves, data aggregation, and device mapping with track playback for location-based devices.

#### 3.1 Log in with Demo Account

Access the Asset Management SaaS Application using the demo account below:

-  **Website URL**: [https://eueam.acceleronix.io/login](https://eueam.acceleronix.io/login)

-  **Account Name** and **Password**: Acceleronix will email you after your purchase. Please contact <evk@acceleronix.io>.

<img  src="/images/saas_login.png"  alt="Login SaaS"  width="700px"  height="auto">

#### 3.2 Find Your Device

1. Navigate to **Device management > Device List**.

2. Locate the IMEI code on the white sticker of your SIMPLI-Kit.

3. Search for the IMEI code in the platform. If the status shows **Online**, your device is successfully connected!

<img  src="/images/search_device_imei.png"  alt="Search device using IMEI"  width="700px"  height="auto">

#### 3.3 Check Device Location (LBS)

1. Click **Details** in the Device List to open the device details.

2. Go to the **Location** tab to see the LBS location data.

<img  src="/images/saas_location.png"  alt="Search device use IMEI"  width="700px"  height="auto">

> **Note**: Location updates every 30 minutes. To refresh manually, click the refresh button in the App control panel, then reload the page to see the updated location.

### 4. Control Your Device with the Wonderfree App

#### 4.1 Obtain the Binding QR Code

1. In the Acceleronix Asset Management SaaS, go to **Device management > Device List > Device Information**.

2. Hover over the QR code icon in the Basic Information section to display the Device QR code.

<img  src="/images/device_qr_code.png"  alt="Device QR Code"  width="700px"  height="auto">

#### 4.2 Download the App and Add Your Device

1. Download the **Wonderfree** app from the app store:

-  **iOS**: [App Store](https://apps.apple.com/gb/app/wonderfree/id6450249586)

-  **Android**: [Google Play](https://play.google.com/store/search?q=wonderfree&c=apps&hl=en_CA&gl=US) or Xiaomi, Vivo, OPPO app galleries.

- More details, please check: [App | Acceleronix](https://core.acceleronix.io/app)

2. Register a new account with your email and log in.

3. Tap **Add Device** in the app, then scan the QR code from the Asset Management SaaS to add your SIMPLI-Kit. It will appear on the app’s home page.

<img  src="/images/add_device.png"  alt="Add Device"  width="700px"  height="auto">

#### 4.3 View and Manage Sensor Data

1. When your device is online, tap it in the Wonderfree app to access the control panel.

2. View real-time sensor and LBS location data from your SIMPLI-Kit.

3. To update sensor data or LBS location, tap the refresh button in the top-right corner of the control panel.
 
<img  src="/images/device_control_panel.jpg"  alt="Device Control Panel"  width="350px"  height="auto">

### 5. Access Acceleronix Developer Center

Please visit <https://core.acceleronix.io> to register an account and login to explore the Acceleronix Developer Center features.

You can follow this [tutorial](https://iot-docs.acceleronix.io/quickStart/register.html) to get started.

## Developer Resources

For additional technical details, documentation, and advanced usage examples, visit the [Acceleronix Developer Portal](https://core.acceleronix.io/).

## Support

If you encounter any issues or have questions about this sample code, please contact [Acceleronix Support](mailto:support@acceleronix.io).