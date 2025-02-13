/*
 * TencentBlueKing is pleased to support the open source community by making
 * 蓝鲸智云 - API 网关(BlueKing - APIGateway) available.
 * Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 *
 *     http://opensource.org/licenses/MIT
 *
 * Unless required by applicable law or agreed to in writing, software distributed under
 * the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
 * either express or implied. See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * We undertake not to change the open source license (MIT license) applicable
 * to the current version of the project delivered to anyone in the future.
 */

package server

import (
	"fmt"
	"net/http"

	"core/pkg/api/microgateway"
	"core/pkg/config"
	"core/pkg/database"
	"core/pkg/middleware"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func checkDatabase(dbConfig *config.Database) error {
	c := database.NewDBClient(dbConfig)
	return c.TestConnection()
}

// NewRouter do the router initialization
func NewRouter(cfg *config.Config) *gin.Engine {
	router := gin.Default()

	router.Use(middleware.RequestID())

	// basic
	// liveness
	router.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})

	// healthz
	router.GET("/healthz", func(c *gin.Context) {
		for _, dbConfig := range cfg.DatabaseMap {
			dbConfig := dbConfig
			// reset the options for check
			dbConfig.MaxIdleConns = 1
			dbConfig.MaxOpenConns = 1
			dbConfig.ConnMaxLifetimeSecond = 60

			err := checkDatabase(&dbConfig)
			if err != nil {
				message := fmt.Sprintf("db connect fail: %s [id=%s host=%s port=%d]",
					err.Error(), dbConfig.ID, dbConfig.Host, dbConfig.Port)
				c.String(http.StatusInternalServerError, message)
				return
			}
		}

		c.JSON(200, gin.H{
			"status": "ok",
		})
	})
	// metrics
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))
	// router.GET("/version", handler.Version)

	microGatewayRouter := router.Group("/api/v1/micro-gateway")
	microGatewayRouter.Use(middleware.APILogger())
	microGatewayRouter.Use(middleware.MicroGatewayInstanceMiddleware())
	microGatewayRouter.GET("/:micro_gateway_instance_id/permissions/", microgateway.QueryPermission)
	microGatewayRouter.GET("/:micro_gateway_instance_id/public_keys/", microgateway.QueryPublicKey)

	return router
}
