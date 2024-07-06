import React, { useRef, useState, useEffect } from "react";
import "./App.css"
import LineChart from "./components/Chart";
import ProgressBar from 'react-customizable-progressbar'

import { useGLTF } from '@react-three/drei'
import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { Environment, OrbitControls } from '@react-three/drei'

import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { AmbientLight } from "three";

let currentDate = new Date();
let year = currentDate.getFullYear();
let month = currentDate.getMonth() + 1; // Months are zero-indexed
let day = currentDate.getDate();

function Scene({ orientation }) {
  const gltf = useLoader(GLTFLoader, './static/rocket2.gltf')
  //[0, 0, - Math.PI / 2]
  //[orientation[0] ? orientation[0] : 0, orientation[1]  ? orientation[1] : 0, orientation[2]  ? orientation[2] - Math.PI / 2 : 0]
  return <primitive object={gltf.scene}
   scale={6}
   rotation={[orientation[0] ? orientation[0] : 0, orientation[1]  ? orientation[1] : 0, orientation[2]  ? orientation[2] - Math.PI / 2 : 0]}
   position={[0, 0, 0]}/>   
}


/*export function Model(props) {
  const { nodes, materials } = useGLTF('./static/rocket.gltf')
  return (
    <group {...props} dispose={null}>
      {/* Render the trup }
      <mesh
        castShadow
        receiveShadow
        geometry={nodes.trup.geometry}
        material={nodes.trup.material}
        rotation={[0, 0, Math.PI / 2]}
      />
      
      {/* Render the Cylinder }
      <mesh
        castShadow
        receiveShadow
        geometry={nodes.Cylinder.geometry}
        material={nodes.Cylinder.material}
        position={[0, -0.4, 0]}
        rotation={[3.1, -0.6, 0]}
        scale={[1, 1, 1]} // Set appropriate scale
      />
      
      {/* Render the finy }
      <mesh
        castShadow
        receiveShadow
        geometry={nodes.finy.geometry}
        material={nodes.finy.material}
        position={[0, -0.3, -0.1]}
        rotation={[-Math.PI / 2, Math.PI / 2, 0]}
        scale={[1, 1, 1]} // Set appropriate scale
      />

    </group>
  )
}

useGLTF.preload('./static/rocket.gltf')*/

function App() {

  //error useStates
  const [flaskError, setFlaskError] = useState(false) //pokud je false, jde flask v pořádku
  const [rocketError, setRocketError] = useState([]) //pokud přijde error z flasku dojde do tohoto listu
  const [rocketDisconected, setRocketDisconected] = useState(false)

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

  const odhad = 725       //kolik odhadujeme dostup rakety v metrech
  const progress = Math.floor(RelativeAltitude / odhad * 100) 

  //make the gps red after getting of the map
  const [makeRed1, setMakeRed1] = useState(false)
  const [makeRed2, setMakeRed2] = useState(false)

  const funcLatitude = (lat) => {
    if (Math.abs(49.239890-lat) < 0.00427) {
      setMakeRed1(false)
      return Math.floor((49.239890-lat)/0.000048)
    }else {
      setMakeRed1(true)
      return (lat > 49.24416 ? -89 : 89)
    }
  }
  const funcLongitude = (lon) => {
    if (Math.abs(16.554873-lon) < 0.0103) {
      setMakeRed2(false)
      return Math.floor((16.554873-lon)/0.000072)
    }else {
      setMakeRed2(true)
      return (lon > 16.565173 ? -143 : 143)
    }
  }

  let previousData = null;
  let consecutiveSameDataCount = 0;
  

  async function get_data() {
    fetch("/data")
    .then(res => res.json())
    .then(data => {

      console.log(data);

      const {latitude, longitude, altitude, sat_count, battery_voltage, battery_temperature, board_temperature, atm_pressure, atm_temperature, atm_humidity, atm_co2_eq, atm_co2_voc, atm_iaq, g_force, gyroscope, acceleration, magnetometer, orientation, force, time, real_time, reference_pressure, compass, relative_altitude, map, fall_speed, time_to_land, momentum, errors} = data
      
      // Compare data with previous data
      if (JSON.stringify(data) === JSON.stringify(previousData)) {
        // Data is the same as previous data
        consecutiveSameDataCount++;

        if (consecutiveSameDataCount >= 5) {
            // Data has been the same for five consecutive times, indicate disconnection
            console.error("Disconnected");
            setRocketDisconected(true)
        }
    } else {
        // Data is different, reset the counter and update previousData
        consecutiveSameDataCount = 0;
        previousData = data;

        setFlaskError(false);
        setRocketDisconected(false)
        setRocketError(errors.length > 0 ? true : false)
        if (errors.length > 0) {
          console.log("problem with rocket you dumbass... ",errors)
        }
        let lat = 49.2406750
        let lon = 16.5567658
        
        //Math.abs(49.239890-lat) < 0.00427 ? Math.floor((49.239890-lat)/0.000048) : ( lat > 49.24416 ? -89 : 89 )
        //Math.abs(16.554873-lon) < 0.0103 ? Math.floor((16.554873-lon)/0.000072) : ( lon > 16.565173 ? -143 : 143)
        setLatitude( funcLatitude(latitude) ) //y
        setLongitude( funcLongitude(longitude) ) //x
        setAltitude(altitude)
        setSatCount(sat_count)
        setBatteryVoltage(battery_voltage)
        setBatteryTemperature(battery_temperature)
        setBoardTemperature(board_temperature)
        setAtmPressure(atm_pressure)
        setAtmTemperature(atm_temperature)
        setAtmHumidity(atm_humidity)
        setAtmCO2Eq(atm_co2_eq)
        setAtmCO2VOC(atm_co2_voc)
        setAtmIAQ(atm_iaq)
        setGForce(g_force)
        setGyroscope(gyroscope)
        setAcceleration(acceleration)
        setMagnetometer(magnetometer)
        setOrientation(orientation)
        setForce(force)
        setTime(time)
        setRealTime(real_time)
        setReferencePressure(reference_pressure)
        setCompass(-3*Math.PI/4 + compass) //-3*Math.PI/4 for arrow to point to north
        setRelativeAltitude(relative_altitude)
        setMap(map)
        setFallSpeed(fall_speed)
        setTimeToLand(time_to_land)
        setMomentum(momentum)
        
        
      }

    })
    .catch(error => setFlaskError(true))
  }
  //send it within 500ms time
  setInterval(async () => get_data(), 1000);

  //reload page when orientation is new
  useEffect(() => {console.log("changed orientation")}, [Orientation]);

  

  //const rucneButton = useRef(null)
  //const senzorButton = useRef(null)

  //setting pressure by buttons
  /*const handleButtonClick = async (endpoint) => {
    try {
      const response = await fetch(endpoint);
      const state = await response.json();
      if (response.ok && !state.error) {
        rucneButton.current.style.display = "none"
        senzorButton.current.style.display = "none"

      } else {
        rucneButton.current.style.background = "red";
        senzorButton.current.style.background = "red";

      }
    } catch (error) {
      console.error("Error occurred:", error);
    }
  };*/


  return (
    <>
    <h5 className="momentum_title">MOMENTUM</h5>
    <hr></hr>
    <div id="data">
      <div id="admin-panel">
        <div id="date">
          <div id="datum">datum: {day}.{month}.{year}</div>
          <div id="čas">čas: {RealTime}</div>
        </div>
        <div className={flaskError || rocketDisconected ? "red-error connected" : "connected"} >
          připojeno: {flaskError || rocketDisconected ? "NE" : "ANO"}
        </div>
        <div className={ flaskError || rocketError || rocketDisconected ? "red-error stav" : "stav"}>
          stav: {flaskError ? "flask Error" : ( rocketError ? "rocket Error" : ( rocketDisconected ? "rocket disconected" : "OK"))}
        </div>
        <div id="gps" style={{ top: `${105 + Latitude}px`,right: `${Longitude}px`, backgroundColor: `${makeRed1 || makeRed2 ? "red" : "#d3ff00"}` }}></div>
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
          <img id="arrow" src=".\static\střelka_good.png" style={{ transform: `rotate(${Time}rad)` }} alt="compass_arrow"/>
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
                  progress={progress}
                  radius={40}
                  initialAnimation={true}
                  strokeColor="#7203FF"
                  strokeLinecap="square"
                  trackStrokeWidth={8}
                  strokeWidth={8}
                  className="progress-bar"
                  >
                    <div className="indicator">
                      <div>{progress}%</div>
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
