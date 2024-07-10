import React, { useRef, useState, useEffect, useCallback } from "react";
import "./App.css"
import LineChart from "./components/Chart";
import ProgressBar from 'react-customizable-progressbar'

import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { Environment, OrbitControls } from '@react-three/drei'

import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'

let currentDate = new Date();
let year = currentDate.getFullYear();
let month = currentDate.getMonth() + 1; // Months are zero-indexed
let day = currentDate.getDate();

function Scene({ orientation }) {
  const gltf = useLoader(GLTFLoader, './static/rocket6.gltf')
  return <primitive object={gltf.scene}
   scale={6}
  rotation={[orientation[2] ? orientation[2] : 0, orientation[1] ? orientation[1] : 0, orientation[0]  ? orientation[0] : 0]}
   position={[0, 0, 0]}/>
}


function App() {

  //error useStates
  const [flaskError, setFlaskError] = useState(false) //pokud je false, jde flask v pořádku
  const [rocketError, setRocketError] = useState([]) //pokud přijde error z flasku dojde do tohoto listu
  const [rocketDisconnected, setRocketDisconnected] = useState(false);

  //data useStates
  const [Latitude, setLatitude] = useState(-1)
  const [Longitude, setLongitude] = useState(-1)
  const [Altitude, setAltitude] = useState(-1)
  const [SatCount, setSatCount] = useState(-1)
  const [BatteryCharge, setBatteryCharge] = useState(-1)
  const [BatteryVoltage, setBatteryVoltage] = useState(-1)
  const [BatteryTemperature, setBatteryTemperature] = useState(-1)
  const [BoardTemperature, setBoardTemperature] = useState(-1)
  const [AtmPressure, setAtmPressure] = useState(-1)
  const [AtmTemperature, setAtmTemperature] = useState(-1)
  const [AtmHumidity, setAtmHumidity] = useState(-1)
  const [AtmCO2Eq, setAtmCO2Eq] = useState(-1)
  const [AtmCO2VOC, setAtmCO2VOC] = useState(-1)
  const [AtmIAQ, setAtmIAQ] = useState(-1)
  const [GForce, setGForce] = useState(-1)
  const [Gyroscope, setGyroscope] = useState([-1, -1, -1])
  const [Acceleration, setAcceleration] = useState([-1, -1, -1])
  const [Magnetometer, setMagnetometer] = useState([-1, -1, -1])
  const [Orientation, setOrientation] = useState([-1, -1, -1])
  const [Force, setForce] = useState([-1, -1, -1])
  const [Time, setTime] = useState(-1)
  const [RealTime, setRealTime] = useState("-1.-1.-2024")
  const [ReferencePressure, setReferencePressure] = useState(-1)
  const [Compass, setCompass] = useState(-3*Math.PI/4)
  const [RelativeAltitude, setRelativeAltitude] = useState(-1)
  const [Map, setMap] = useState([-1, -1])
  const [FallSpeed, setFallSpeed] = useState(-1)
  const [TimeToLand, setTimeToLand] = useState(-1)
  const [Momentum, setMomentum] = useState(-1)

  const [GPSX, setGPSX] = useState(72)
  const [GPSY, setGPSY] = useState(44)

  const odhad = 725       //kolik odhadujeme dostup rakety v metrech
  const [maxProgress, setMaxProgress] = useState(-1) //var for progress wheel

  //make the gps red after getting of the map
  const [makeRed1, setMakeRed1] = useState(false)
  const [makeRed2, setMakeRed2] = useState(false)

   
    

  const funcLatitude = (lat) => {
    let stred_mapy = 49.239890
    if (Math.abs(stred_mapy-lat) < 0.00427) {
      setMakeRed1(false)
      return Math.floor((stred_mapy-lat)/0.000048)
    }else {
      setMakeRed1(true)
      return (lat > 49.24416 ? -89 : 89)
    }
  }
  const funcLongitude = (lon) => {
    let stred_mapy = 16.554873 
    if (Math.abs(stred_mapy-lon) < 0.0103) {
      setMakeRed2(false)
      return Math.floor((stred_mapy-lon)/0.000072)
    }else {
      setMakeRed2(true)
      return (lon > 16.565173 ? -143 : 143)
    }
  }

  //vars for setRocketDisconnected useState
  const [previousData, setPreviousData] = useState(null);
  const [consecutiveSameDataCount, setConsecutiveSameDataCount] = useState(0);


const fetchData = useCallback(async () => {
  try {
    const res = await fetch("/data");
    const newData = await res.json();

    //console.log(newData);

    if (JSON.stringify(newData) === JSON.stringify(previousData)) {
      setConsecutiveSameDataCount(count => count + 1);

      //if the data is same 5 times it is disconnected
      if (consecutiveSameDataCount >= 5) {
        console.error("Disconnected");
        setRocketDisconnected(true);
      }
    } else {
      setConsecutiveSameDataCount(0);
      setPreviousData(newData);

      setFlaskError(false);
      setRocketDisconnected(false);
      setRocketError(newData.errors.length > 0);

      if (newData.errors.length > 0) {
        console.error("Problem with rocket: ", newData.errors);
      }

      const {
        latitude, longitude, altitude, sat_count, battery_voltage,
        battery_temperature, board_temperature, atm_pressure, atm_temperature,
        atm_humidity, atm_co2_eq, atm_co2_voc, atm_iaq, g_force, gyroscope,
        acceleration, magnetometer, orientation, force, time, real_time,
        reference_pressure, compass, relative_altitude, map, fall_speed,
        time_to_land, momentum
      } = newData;

      setLatitude(latitude);
      setLongitude(longitude);
      setAltitude(altitude);
      setSatCount(sat_count);
      setBatteryVoltage(battery_voltage);
      setBatteryTemperature(battery_temperature);
      setBoardTemperature(board_temperature);
      setAtmPressure(atm_pressure);
      setAtmTemperature(atm_temperature);
      setAtmHumidity(atm_humidity);
      setAtmCO2Eq(atm_co2_eq);
      setAtmCO2VOC(atm_co2_voc);
      setAtmIAQ(atm_iaq);
      setGForce(g_force);
      setGyroscope(gyroscope);
      setAcceleration(acceleration);
      setMagnetometer(magnetometer);
      setOrientation(orientation);
      setForce(force);
      setTime(time);
      setRealTime(real_time);
      setReferencePressure(reference_pressure);
      setCompass(-3 * Math.PI / 4 + compass); //to set the compass to the north -3 * Math.PI / 4 is needed
      setRelativeAltitude(relative_altitude);
      setMap(map);
      setFallSpeed(fall_speed);
      setTimeToLand(time_to_land);
      setMomentum(momentum);

     

      setGPSX(funcLongitude(longitude))
      setGPSY(funcLatitude(latitude))

      //for the progress wheel for height
      let progress = Math.floor(RelativeAltitude / odhad * 100)
      if (progress > maxProgress) {
        setMaxProgress(progress);
      } 

    }
  } catch (error) {
    setFlaskError(true);
  }
}, [previousData, consecutiveSameDataCount]);

useEffect(() => {
  const interval = setInterval(fetchData, 400);
  return () => clearInterval(interval);
}, [fetchData]);
  

  const rucneButton = useRef(null)
  //const senzorButton = useRef(null)

  //setting pressure by buttons
  const handleButtonClick = async (endpoint) => {
    try {
      const response = await fetch(endpoint);
      const state = await response.json();
      if (response.ok && !state.error) {
        rucneButton.current.style.display = "none"
        //senzorButton.current.style.display = "none"

      } else {
        rucneButton.current.style.background = "red";
        //senzorButton.current.style.background = "red";

      }
    } catch (error) {
      console.error("Error occurred:", error);
    }
  };


  return (
    <>
    <span id="navbar">
      <h5 className="momentum_title">MOMENTUM</h5>
      <button ref={rucneButton} onClick={() => handleButtonClick("/set_pressure")}>P</button>
    </span>
    <hr></hr>
    <div id="data">
      <div id="admin-panel">
        <div id="date">
          <div id="datum">datum: {day}.{month}.{year}</div>
          <div id="čas">čas: {RealTime}</div>
        </div>
        <div className={flaskError || rocketDisconnected ? "red-error connected" : "connected"} >
          připojeno: {flaskError || rocketDisconnected ? "NE" : "ANO"}
        </div>
        <div className={ flaskError || rocketError || rocketDisconnected ? "red-error stav" : "stav"}>
          stav: {flaskError ? "flask Error" : ( rocketError ? "rocket Error" : ( rocketDisconnected ? "rocket disconected" : "OK"))}
        </div>
        <table>
          <tr id="tb_row_down">
            <td className="gps">zem. šířka: <div>{Longitude}</div></td>
            <td className="gps">zem. délka: <div>{Latitude}</div></td>
          </tr>
          <tr>
            <td className="gps">zem. výška: {Altitude}m</td>
            <td className="gps">satelity: {SatCount}</td>
          </tr>
        </table>
        <div id="gps" style={{ top: `${105 + GPSY}px`,right: `${GPSX}px`, backgroundColor: `${makeRed1 || makeRed2 ? "red" : "#d3ff00"}` }}></div>
        <img id="mapa" src=".\static\map_gps.png" alt="map" />
      </div>
      <div id="press-chart">
        <div id="press-title">graf tlaku v závislosti na čase</div>
        <hr></hr>
        <LineChart time={Time} pressure={AtmPressure}/>
      </div>
      <div id="rocket-model">
        <div id="name-model-rakety">model rakety</div>
        <hr></hr>
        <div style={{ width: '100%', height: '100%' }}>
          <Canvas>
            <Suspense fallback={null}>
              <Scene orientation={Orientation}/>
              <OrbitControls/>
              <Environment preset="sunset"/>
            </Suspense>
          </Canvas>
        </div>
        <div id="main_compass">
          <img id="compass" src=".\static\compass_empty_fr.png" alt="compass"/>
          <img id="arrow" src=".\static\střelka_good.png" style={{ transform: `rotate(${Compass}rad)` }} alt="compass_arrow"/>
        </div>
      </div>
      <div id="xyz">
        <div id="left_xyz">
          <div id="akcelerace">
            <div className="underline">akcelerace</div>
            <div>x: {Acceleration[0]} G</div>
            <div>y: {Acceleration[1]} G</div>
            <div>z: {Acceleration[2]} G</div>
            {/*<div id="smol">(síla působící na raketu 1.2 N)</div>*/}
          </div>
          <div id="gyroskop">
            <div className="underline">gyroskop</div>
            <div>x: {Gyroscope[0]} °/s</div>
            <div>y: {Gyroscope[1]} °/s</div>
            <div>z: {Gyroscope[2]} °/s</div>
          </div>
        </div>
        <div id="right_xyz">
          <div id="lineární_akcelerace">
            <div className="underline">síla působící na raketu</div>
            <div>x: {Force[0]} N</div>
            <div>y: {Force[1]} N</div>
            <div>z: {Force[2]} N</div>
          </div>
          <div id="magnetometr">
            <div className="underline">magnetometr</div>
            <div>x: {Magnetometer[0]} µT</div>
            <div>y: {Magnetometer[1]} µT</div>
            <div>z: {Magnetometer[2]} µT</div>
          </div>
        </div>
      </div>
      <div id="main-data">
        <div id="data-get">
          <div className="heading">
            <div className="temp">teplota: {AtmTemperature} °C</div>
            <div>tlak: {AtmPressure} hPa</div>
          </div>
          <div id="bottom_data">
            <table>
              <tr>
                <td className="spec-data no_border">teplota hl. desky: </td>
                <td className="nums no_border">{BoardTemperature} °C</td>
              </tr>
              <tr>
                <td className="spec-data">teplota baterie: </td>
                <td className="nums">{BatteryTemperature} °C</td>
              </tr>    
              <tr>
                <td className="spec-data">napětí baterie: </td>
                <td className="nums">{BatteryVoltage} V</td>
              </tr>
              <tr>
                <td className="spec-data">vlhkost: </td>
                <td className="nums">{AtmHumidity} %</td>
              </tr>
              <tr>
                <td className="spec-data no_border">C02 ekv. </td>
                <td className="nums no_border">{AtmCO2Eq} ppm</td>
              </tr>
              <tr>
                <td className="spec-data">C02 VOC </td>
                <td className="nums">{AtmCO2VOC} ppm</td>
              </tr>
              <tr>
                <td className="spec-data">IAQ </td>
                <td className="nums">{AtmIAQ}</td>
              </tr>
            </table>
            <div id="right_side_height_chart">
              <div id="height2">výška nad zemí: </div>
              <div id="height_num">{RelativeAltitude} m</div>              
              <ProgressBar
                  progress={maxProgress}
                  radius={40}
                  initialAnimation={true}
                  strokeColor="#7203FF"
                  strokeLinecap="square"
                  trackStrokeWidth={8}
                  strokeWidth={8}
                  className="progress-bar"
                  >
                    <div className="indicator">
                      <div>{maxProgress}%</div>
                    </div>
                  </ProgressBar>
              <div id="proc-odh2">dosažení odhadu {odhad} m</div>
            </div>
          </div>
        </div>
      </div>
      <div id="footer">
        <div id="const">
          <div className="construcked">raketu konstruovali: Benedikt Hlaváček, Michal Friml, Jakub Stříbrný, Lukáš Cichý, Martin Zuzek
          </div>
          <div className="construcked">Czech Rocket Chalenge 2024</div>
        </div>
        <div id="images">
          <img id="momentum-logo" src=".\static\momentum_hezci.svg" alt="school logo" />
          <div id="between-bar"></div>
          <img id="school-logo" src=".\static\logo gymple nádherné.png" alt="school logo" />
        </div>
      </div>
    </div>
    </>
  );
}

export default App;
