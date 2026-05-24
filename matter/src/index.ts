#!/usr/bin/env node
/**
 * @license
 * Copyright 2022-2026 Matter.js Authors
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * This example shows how to create a simple on-off Matter device as a light or as a socket.
 * It can be used as CLI script and starting point for your own device node implementation.
 * This example is CJS conform and do not use top level await's.
 */

import {
  DeviceTypeId,
  Endpoint,
  Environment,
  Logger,
  ServerNode,
  StorageService,
  Time,
  VendorId,
} from "@matter/main";
import { DimmableLightDevice } from "@matter/main/devices";
import net from "net";

const logger = Logger.get("DeviceNode");
const SOCKET_PATH = "/run/matrix/matrix.sock";

async function main() {
  /** Initialize configuration values */
  const {
    deviceName,
    vendorName,
    passcode,
    discriminator,
    vendorId,
    productName,
    productId,
    port,
    uniqueId,
  } = await getConfiguration();

  /**
   * Create a Matter ServerNode, which contains the Root Endpoint and all relevant data and configuration
   */
  const server = await ServerNode.create({
    // Required: Give the Node a unique ID which is used to store the state of this node
    id: uniqueId,

    // Provide Network relevant configuration like the port
    // Optional when operating only one device on a host, Default port is 5540
    network: {
      port,
    },

    // Provide Commissioning relevant settings
    // Optional for development/testing purposes
    commissioning: {
      passcode,
      discriminator,
    },

    // Provide Node announcement settings
    // Optional: If Omitted some development defaults are used
    productDescription: {
      name: deviceName,
      deviceType: DeviceTypeId(DimmableLightDevice.deviceType),
    },

    // Provide defaults for the BasicInformation cluster on the Root endpoint
    // Optional: If Omitted some development defaults are used
    basicInformation: {
      vendorName,
      vendorId: VendorId(vendorId),
      nodeLabel: productName,
      productName,
      productLabel: productName,
      productId,
      serialNumber: `matterjs-${uniqueId}`,
      uniqueId,
    },
  });

  /**
   * Matter Nodes are a composition of endpoints. Create and add a single endpoint to the node. This example uses the
   * OnOffLightDevice or OnOffPlugInUnitDevice depending on the value of the type parameter. It also assigns this Part a
   * unique ID to store the endpoint number for it in the storage to restore the device on restart.
   * In this case we directly use the default command implementation from matter.js. Check out the DeviceNodeFull example
   * to see how to customize the command handlers.
   */
  const endpoint = new Endpoint(DimmableLightDevice, { id: "dimmable" });
  await server.add(endpoint);

  const client = net.createConnection(SOCKET_PATH);

  client.on("data", (data) => {
    const msg = data.toString().trim();
    if (msg === "on") {
      endpoint.set({ onOff: { onOff: true } });
    } else if (msg === "off") {
      endpoint.set({ onOff: { onOff: false } });
    } else {
      const percent = parseInt(msg);

      if (Number.isNaN(percent)) {
        console.error(`Unknown command: ${msg}`);
      } else {
        // Matter uses 0–254 for currentLevel, not 0–100
        const level = Math.round((percent / 100) * 254);
        endpoint.set({ levelControl: { currentLevel: level } });
      }
    }
  });

  client.on("error", (err) => {
    console.error("Connection error:", err.message);
  });

  /**
   * Register state change handlers and events of the node for identify and onoff states to react to the commands.
   * If the code in these change handlers fail then the change is also rolled back and not executed and an error is
   * reported back to the controller.
   */
  endpoint.events.identify.startIdentifying.on(() => {
    console.warn(`Run identify logic, ideally blink a light every 0.5s ...`);
  });

  endpoint.events.identify.stopIdentifying.on(() => {
    console.warn(`Stop identify logic ...`);
  });

  endpoint.events.onOff.onOff$Changed.on((value) => {
    // executeCommand(value ? "on" : "off");
    const state = value ? "on" : "off";
    console.warn(`OnOff is now ${state}`);
    client.write(state);
  });

  endpoint.events.levelControl.currentLevel$Changed.on((value) => {
    const percent = Math.round(((value ?? 0) / 254) * 100);
    console.warn(`Brightness is now ${percent}%`);
    client.write(`${percent}`);
  });

  /**
   * Log the endpoint structure for debugging reasons and to allow to verify anything is correct
   */
  logger.info(server);

  /**
   * In order to start the node and announce it into the network we use the run method which resolves when the node goes
   * offline again because we do not need anything more here. See the Full example for other starting options.
   * The QR Code is printed automatically.
   */
  await server.run();
}

main().catch((error) => console.error(error));

/*********************************************************************************************************
 * Convenience Methods
 *********************************************************************************************************/

async function getConfiguration() {
  const environment = Environment.default;

  const storageService = environment.get(StorageService);
  console.warn(`Storage location: ${storageService.location} (Directory)`);
  console.warn(
    'Use the parameter "--storage-path=NAME-OR-PATH" to specify a different storage location in this directory, use --storage-clear to start with an empty storage.',
  );

  const storageManager = await storageService.open("device");
  const deviceStorage = storageManager.createContext("data");

  const deviceName = "Wall LED Matrix";
  const vendorName = "Oomfie Networks";

  // values from the example script, unchanged
  const passcode = 20202021;
  const discriminator = 3840;
  // product name / id and vendor id should match what is in the device certificate
  const vendorId = 0xfff1; // development only VID
  const productName = "Wall LED Matrix";
  const productId = 0x8000; // development PID

  const port = 5540;

  const uniqueId = (await deviceStorage.get("uniqueid", Time.nowMs)).toString();

  // Persist basic data to keep them also on restart
  await deviceStorage.set({
    uniqueid: uniqueId,
  });

  await storageManager.close();

  return {
    deviceName,
    vendorName,
    passcode,
    discriminator,
    vendorId,
    productName,
    productId,
    port,
    uniqueId,
  };
}
