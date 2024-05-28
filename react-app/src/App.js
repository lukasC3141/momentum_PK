import React, { useRef, useState } from "react";
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

function Scene() {
  const gltf = useLoader(GLTFLoader, './static/rocket2.gltf')
  return <primitive object={gltf.scene}
   scale={8}
   rotation={[0, 0, - Math.PI / 2]}
   position={[0, 1, 0]}/>   
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

  const [flaskError, setFlaskError] = useState(false) //pokud je false, jde flask v pořádku
  const [rocketError, setRocketError] = useState(false)
  const [rocketDisconected, setRocketDisconected] = useState(false)
  const [momentums, setMomentum] = useState(-1)
  const [pressure, setPressure] = useState(-1)
  const [pressure_reference, setPressure_reference] = useState(-1)
  const [speed_of_falls, setSpeed_of_fall] = useState(-1)
  const [reference_height, setReference_height] = useState(-1)
  const [temperature, setTemparature] = useState(-1)
  const [voltage, setVoltage] = useState(-1)
  const [time, setTime] = useState(0)
  const [height, setHeight] = useState(0)
  const odhad = 725       //kolik odhadujeme dostup rakety v metrech
  const progress = Math.floor(reference_height / odhad * 100) 


  let previousData = null;
  let consecutiveSameDataCount = 0;

  async function get_data() {
    fetch("/data")
    .then(res => res.json())
    .then(data => {
      const {error, pressure, pressure_reference, reference_height, temperature, time, voltage, speed_of_fall, momentum} = data[0]
      
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
        setRocketError(error)
        setPressure(pressure)
        setPressure_reference(pressure_reference)
        setReference_height(reference_height)
        setTemparature(temperature)
        setVoltage(voltage)
        setSpeed_of_fall(speed_of_fall)
        setMomentum(momentum)  // try
        setTime(time);

        console.log(data);
        /*console.log("momentum", momentum);
        console.log("pressure", pressure);
        console.log("time", time);*/
    }

    })
    .catch(error => setFlaskError(true))
  }
  //send it within 500ms time
  setInterval(async () => get_data(), 1000);


  const rucneButton = useRef(null)
  const senzorButton = useRef(null)

  //setting pressure by buttons
  const handleButtonClick = async (endpoint) => {
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
  };

  return (
    <>
    <h5 className="momentum_title">MOMENTUM</h5>
    <hr></hr>
    <div id="data">
      <div id="admin-panel">
        <div className={flaskError || rocketDisconected ? "red-error connected" : "connected"} >
          připojeno: {flaskError || rocketDisconected ? "NE" : "ANO"}
        </div>
        <div className={ flaskError || rocketError || rocketDisconected ? "red-error stav" : "stav"}>
          stav: {flaskError ? "flask Error" : ( rocketError ? "rocket Error" : ( rocketDisconected ? "rocket disconected" : "OK"))}
        </div>
        <div id="time">
          čas: {time}s
        </div>
        <div id="pressure-setting">
          nastavení tlaku:
        </div>
        <div id="press-buttons">
          <button ref={rucneButton} onClick={() => handleButtonClick('/load_pressure')}>
            <span className="button_top">RUČNÍ</span>
          </button>
          <button ref={senzorButton} onClick={() => handleButtonClick('/set_pressure')}>
          <span className="button_top">ZE SENZORU</span>
          </button>
        </div>
        <div id="ref-pressure">
          referenční tlak: {pressure_reference} hPa
        </div>
      </div>
      <div id="press-chart">
        <div id="press-title">graf tlaku v závislosti na čase</div>
        <hr></hr>
        <LineChart time={time} pressure={pressure}/>
      </div>
      <div id="rocket-model">
        <div id="name-model-rakety">model rakety</div>
        <hr></hr>
        <div style={{ width: '100%', height: '100%' }}>
          <Canvas>
            <Suspense fallback={null}>
              <Scene />
              <OrbitControls />
              <Environment preset="sunset"/>
            </Suspense>
          </Canvas>
        </div>
        {/* <img id="rocket-model-close" src="./static/rocket-model.png" alt="rocket"></img>*/}
      </div>
      <div id="height-chart">
        <div className="ref-pressure">*vypočítaná z tlaku</div>
        <div id="height">*výška: {reference_height} m</div>
        <div id="odhad">odhad dosažené výšky: {odhad} m</div>
        
        <ProgressBar
            progress={progress}
            radius={100}
            initialAnimation={true}
            strokeColor="#7203FF"
            strokeLinecap="square"
            trackStrokeWidth={18}
            className="progress-bar"
            >
              <div className="indicator">
                <div>{progress}%</div>
            </div>
            </ProgressBar>
        <div id="proc-odh">procentuální dosažení odhadu</div>
      </div>
      <div id="main-data">
        <div id="data-get">
        <table>
          <tr>
            <td className="spec-data">teplota: </td>
            <td className="nums">{temperature} °C</td>
          </tr>
          <tr>
            <td className="spec-data">napětí: </td>
            <td className="nums">{voltage} V</td>
          </tr>
          <tr>
            <td className="spec-data">tlak: </td>
            <td className="nums">{pressure} hPa</td>
          </tr>
          <tr>
            <td className="spec-data">rychlost: </td>
            <td className="nums">{speed_of_falls} m/s</td>
          </tr>
          <tr>
            <td className="spec-data">hybnost: </td>
            <td className="nums">{momentums} kg*m/s</td>
            
          </tr>
        </table>
        </div>   
      </div>
      <div id="footer">
        <div id="const">
          <div className="construcked">raketu konstruovali: Benedikt Hlaváček, Michal Friml, Jakub Stříbrný, Lukáš Cichý, Martin Zuzek
          </div>
          <div className="construcked">Czech Rocket Chalenge 2024</div>
        </div>
        <div id="images">
          <img id="school-logo1" src="./static/znak-removebg-preview.png" alt="school logo" />
          <div id="between-bar"></div>
          <img id="school-logo2" src="./static/znak-removebg-preview.png" alt="school logo" />
        </div>
      </div>
    </div>
    </>
  );
}

export default App;
