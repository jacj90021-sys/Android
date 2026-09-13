/*
 * Copyright (c) 2025 DuckDuckGo
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.duckduckgo.widget

import android.content.Context
import android.view.View
import android.widget.RemoteViews
import com.duckduckgo.app.browser.R
import com.duckduckgo.common.ui.store.AppBrandDesignUpdateToggles
import com.duckduckgo.common.utils.DispatcherProvider
import kotlinx.coroutines.withContext
import javax.inject.Inject

internal fun resolveSearchBarBackground(
    widgetTheme: WidgetTheme,
    isAddressBarRebrandEnabled: Boolean,
): Int = when (widgetTheme) {
    WidgetTheme.LIGHT -> if (isAddressBarRebrandEnabled) {
        R.drawable.search_widget_background_rebrand_light
    } else {
        R.drawable.search_widget_background_light
    }
    WidgetTheme.DARK -> if (isAddressBarRebrandEnabled) {
        R.drawable.search_widget_background_rebrand_dark
    } else {
        R.drawable.search_widget_background_dark
    }
    WidgetTheme.SYSTEM_DEFAULT -> if (isAddressBarRebrandEnabled) {
        R.drawable.search_widget_background_rebrand_daynight
    } else {
        R.drawable.search_widget_background_daynight
    }
}

class SearchWidgetConfigurator @Inject constructor(
    private val dispatcherProvider: DispatcherProvider,
    private val appBrandDesignUpdateToggles: AppBrandDesignUpdateToggles,
) {

    suspend fun populateRemoteViews(
        context: Context,
        remoteViews: RemoteViews,
        fromFavWidget: Boolean,
        fromSearchOnlyWidget: Boolean = false,
        widgetTheme: WidgetTheme,
    ) {
        withContext(dispatcherProvider.main()) {
            remoteViews.setInt(
                if (fromFavWidget) R.id.widgetSearchBarContainer else R.id.widgetContainer,
                "setBackgroundResource",
                resolveSearchBarBackground(
                    widgetTheme = widgetTheme,
                    isAddressBarRebrandEnabled = appBrandDesignUpdateToggles.addressBar().isEnabled(),
                ),
            )
            // Voice search and Duck.ai are removed; always show the plain search affordance.
            remoteViews.setViewVisibility(R.id.voiceSearch, View.GONE)
            remoteViews.setViewVisibility(R.id.duckAi, View.GONE)
            remoteViews.setViewVisibility(R.id.separator, View.GONE)
            remoteViews.setViewVisibility(R.id.search, View.VISIBLE)
        }
    }
}
